"""Integration tests for Banesco client."""

from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

import pytest

from infrastructure.external.banesco_client import (
    BanescoAuthError,
    BanescoClient,
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
            token_url="https://api.banesco.com/oauth/token",
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

    @pytest.mark.asyncio
    async def test_get_token_success(self, oauth_client: BanescoOAuth2Client) -> None:
        """Test successful token retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            token = await oauth_client.get_token()

        assert token == "new-access-token"
        assert oauth_client._cached_token == "new-access-token"

    @pytest.mark.asyncio
    async def test_get_token_auth_error(
        self, oauth_client: BanescoOAuth2Client
    ) -> None:
        """Test token retrieval with authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(BanescoAuthError):
                await oauth_client.get_token()

    @pytest.mark.asyncio
    async def test_token_caching(self, oauth_client: BanescoOAuth2Client) -> None:
        """Test that token is cached and reused."""
        oauth_client._cached_token = "cached-token"
        oauth_client._token_expires_at = 9999999999.0  # Far future

        token = await oauth_client.get_token()

        assert token == "cached-token"


class TestBanescoClient:
    """Test suite for BanescoClient."""

    @pytest.fixture
    def mock_oauth_client(self) -> Mock:
        """Create mock OAuth2 client."""
        client = Mock(spec=BanescoOAuth2Client)
        client.get_token = AsyncMock(return_value="test-access-token")
        return client

    @pytest.fixture
    def banesco_client(self, mock_oauth_client: Mock) -> BanescoClient:
        """Create BanescoClient instance."""
        return BanescoClient(
            base_url="https://api.banesco.com",
            oauth_client=mock_oauth_client,
        )

    @pytest.mark.asyncio
    async def test_verify_transaction_success(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test successful transaction verification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "approved",
            "reference": "REF123",
            "amount": 100.50,
            "verification_code": "ABC123",
        }

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await banesco_client.verify_transaction("REF123")

        assert result["status"] == "approved"
        assert result["reference"] == "REF123"
        assert result["amount"] == 100.50

    @pytest.mark.asyncio
    async def test_verify_transaction_rate_limit(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test rate limit handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            with pytest.raises(BanescoRateLimitError) as exc_info:
                await banesco_client.verify_transaction("REF123")

        assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_verify_transaction_timeout(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test timeout handling."""
        import httpx

        with patch(
            "httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Timeout")
        ):
            with pytest.raises(BanescoTimeoutError):
                await banesco_client.verify_transaction("REF123")

    @pytest.mark.asyncio
    async def test_verify_transaction_retry_logic(
        self, banesco_client: BanescoClient
    ) -> None:
        """Test retry logic on temporary failures."""
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "status": "approved",
            "reference": "REF123",
        }

        with patch(
            "httpx.AsyncClient.get",
            side_effect=[mock_response_fail, mock_response_success],
        ):
            result = await banesco_client.verify_transaction("REF123")

        assert result["status"] == "approved"

    @pytest.mark.asyncio
    async def test_query_balance_success(self, banesco_client: BanescoClient) -> None:
        """Test successful balance query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "account_number": "0134123456781234567890",
            "balance": 5000.00,
            "currency": "VES",
        }

        with patch("httpx.AsyncClient.get", return_value=mock_response):
            result = await banesco_client.query_balance("0134123456781234567890")

        assert result["balance"] == 5000.00
        assert result["currency"] == "VES"
