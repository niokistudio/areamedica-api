"""Authentication API routes."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.auth_dto import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from application.services.auth_service import AuthService
from domain.entities.user import User
from infrastructure.database.connection import get_db_session
from infrastructure.database.repositories import UserRepository

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Dependency to get auth service."""
    return AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Dependency to get current authenticated user."""
    token = credentials.credentials

    try:
        user_id = auth_service.extract_user_id_from_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user."""
    user_repo = UserRepository(session)

    # Check if user already exists
    existing_user = await user_repo.get_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    password_hash = auth_service.get_password_hash(request.password)
    new_user = User(
        id=uuid4(),
        email=request.email,
        password_hash=password_hash,
        full_name=request.full_name,
        is_active=True,
        permissions=[],
    )

    created_user = await user_repo.create(new_user)
    await session.commit()

    return UserResponse(
        id=str(created_user.id),
        email=created_user.email,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        permissions=[p.name for p in created_user.permissions],
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Login user and return JWT token."""
    user_repo = UserRepository(session)

    # Get user by email
    user = await user_repo.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not auth_service.verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create access token
    permissions = [p.name for p in user.permissions]
    access_token = auth_service.create_access_token(
        user_id=user.id, email=user.email, permissions=permissions
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        permissions=[p.name for p in current_user.permissions],
    )
