"""Banesco API client with OAuth 2.0 authentication."""

import asyncio
from datetime import datetime, timedelta

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger()


class BanescoOAuth2Client:
    """OAuth 2.0 client for Banesco authentication."""

    def __init__(self, auth_url: str, client_id: str, client_secret: str) -> None:
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: str | None = None
        self.token_expires_at: datetime | None = None
        self._lock = asyncio.Lock()

    async def get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary."""
        async with self._lock:
            # Check if current token is still valid
            if (
                self.access_token
                and self.token_expires_at
                and datetime.utcnow() < self.token_expires_at
            ):
                return self.access_token

            # Request new token
            await self._request_new_token()
            return self.access_token or ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _request_new_token(self) -> None:
        """Request new access token from Banesco OAuth server."""
        logger.info("Requesting new Banesco OAuth token")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.auth_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    timeout=30,
                )
                response.raise_for_status()

                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)

                # Set expiration with 60 second buffer
                self.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=expires_in - 60
                )

                logger.info(
                    "Successfully obtained Banesco OAuth token",
                    expires_in=expires_in,
                )

            except httpx.HTTPStatusError as e:
                logger.error(
                    "Failed to obtain Banesco OAuth token",
                    status_code=e.response.status_code,
                    error=str(e),
                )
                raise
            except Exception as e:
                logger.error(
                    "Unexpected error obtaining Banesco OAuth token", error=str(e)
                )
                raise


class BanescoAPIError(Exception):
    """Base exception for Banesco API errors."""

    pass


class BanescoTimeoutError(Exception):
    """Raised when Banesco API request times out."""

    pass


class BanescoRateLimitError(Exception):
    """Raised when Banesco API rate limit is exceeded."""

    pass


class BanescoNotFoundError(Exception):
    """Raised when transaction is not found in Banesco."""

    pass


class BanescoClient:
    """Client for interacting with Banesco API."""

    def __init__(
        self,
        base_url: str,
        oauth_client: BanescoOAuth2Client,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url
        self.oauth_client = oauth_client
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

    async def _get_headers(self) -> dict[str, str]:
        """Get request headers with OAuth 2.0 token."""
        access_token = await self.oauth_client.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(BanescoAPIError),
    )
    async def get_transaction_status(self, transaction_id: str) -> dict | None:
        """Get transaction status from Banesco API.

        Args:
            transaction_id: Transaction ID to query

        Returns:
            Transaction data dict or None if not found

        Raises:
            BanescoTimeoutError: If request times out
            BanescoRateLimitError: If rate limit exceeded
            BanescoAPIError: For other API errors
        """
        try:
            headers = await self._get_headers()
            response = await self.client.get(
                f"{self.base_url}/transactions/{transaction_id}",
                headers=headers,
            )

            if response.status_code == 200:
                logger.info(
                    "Successfully retrieved transaction from Banesco",
                    transaction_id=transaction_id,
                )
                return response.json()

            if response.status_code == 404:
                logger.warning(
                    "Transaction not found in Banesco",
                    transaction_id=transaction_id,
                )
                raise BanescoNotFoundError(f"Transaction {transaction_id} not found")

            if response.status_code == 429:
                logger.warning(
                    "Rate limited by Banesco",
                    transaction_id=transaction_id,
                )
                raise BanescoRateLimitError("Banesco API rate limit exceeded")

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as e:
            logger.error(
                "Banesco API timeout",
                transaction_id=transaction_id,
                error=str(e),
            )
            raise BanescoTimeoutError(
                f"Timeout querying Banesco for transaction {transaction_id}"
            ) from e

        except (BanescoNotFoundError, BanescoRateLimitError):
            raise

        except Exception as e:
            logger.error(
                "Banesco API error",
                transaction_id=transaction_id,
                error=str(e),
            )
            raise BanescoAPIError(f"Error querying Banesco API: {e}") from e

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "BanescoClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit."""
        await self.close()
