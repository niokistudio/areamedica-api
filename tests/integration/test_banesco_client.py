"""Integration tests for Banesco client."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from infrastructure.external.banesco_client import (
    BanescoClient,
    BanescoNotFoundError,
    BanescoOAuth2Client,
    BanescoRateLimitError,
    BanescoTimeoutError,
)


class TestBanescoOAuth2Client:
    """Test suite for BanescoOAuth2Client."""

    @pytest.fixture
    def oauth_client(self) -> BanescoOAuth2Client:
        """Create OAuth2 client instance."""
        return BanescoOAuth2Client(
            auth_url="https://api.banesco.com/oauth/token",
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

    @pytest.mark.asyncio
    async def test_get_access_token_success(
        self, oauth_client: BanescoOAuth2Client
    ) -> None:
        """Test successful token retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            token = await oauth_client.get_access_token()

        assert token == "new-access-token"
        assert oauth_client.access_token == "new-access-token"


class TestBanescoClient:
    """Test suite for BanescoClient."""

    @pytest.fixture
    def mock_oauth_client(self) -> Mock:
        """Create mock OAuth2 client."""
        client = Mock(spec=BanescoOAuth2Client)
        client.get_access_token = AsyncMock(return_value="test-access-token")
        return client

    @pytest.fixture
    def banesco_client(self, mock_oauth_client: Mock) -> BanescoClient:
        """Create BanescoClient instance."""
        return BanescoClient(
            base_url="https://api.banesco.com",
            oauth_client=mock_oauth_client,
        )

    @pytest.mark.asyncio
    async def test_get_transaction_status_success(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test successful transaction status retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "approved",
            "reference": "REF123",
            "amount": 100.50,
        }

        banesco_client.client.get = AsyncMock(return_value=mock_response)
        result = await banesco_client.get_transaction_status("REF123")

        assert result["status"] == "approved"
        assert result["reference"] == "REF123"
        assert result["amount"] == 100.50

    @pytest.mark.asyncio
    async def test_get_transaction_status_not_found(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test transaction not found."""
        mock_response = Mock()
        mock_response.status_code = 404

        banesco_client.client.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(BanescoNotFoundError):
            await banesco_client.get_transaction_status("REF123")

    @pytest.mark.asyncio
    async def test_get_transaction_status_rate_limit(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test rate limit handling."""
        mock_response = Mock()
        mock_response.status_code = 429

        banesco_client.client.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(BanescoRateLimitError):
            await banesco_client.get_transaction_status("REF123")

    @pytest.mark.asyncio
    async def test_get_transaction_status_timeout(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test timeout handling."""
        banesco_client.client.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        
        with pytest.raises(BanescoTimeoutError):
            await banesco_client.get_transaction_status("REF123")
