"""
Tests for Dropbox OAuth2 authentication - AD-5
Tests OAuth2 flow and session management
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from app import auth


class TestOAuth2AuthURL:
    """Tests for OAuth2 authorization URL generation"""

    @pytest.mark.asyncio
    async def test_generate_auth_url_redirects_to_dropbox(self, client: AsyncClient):
        """Test 1: /auth/dropbox/login redirects to Dropbox OAuth2"""
        response = await client.get("/auth/dropbox/login", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "dropbox.com/oauth2/authorize" in response.headers["location"]

    @pytest.mark.asyncio
    async def test_auth_url_includes_app_key(self, client: AsyncClient):
        """Test 2: Auth URL includes correct app_key"""
        response = await client.get("/auth/dropbox/login", follow_redirects=False)
        location = response.headers["location"]
        assert "client_id=rvsal3as0j73d3y" in location

    @pytest.mark.asyncio
    async def test_auth_url_includes_redirect_uri(self, client: AsyncClient):
        """Test 3: Auth URL includes redirect_uri"""
        response = await client.get("/auth/dropbox/login", follow_redirects=False)
        location = response.headers["location"]
        assert "redirect_uri=" in location
        # URL-encoded version of /auth/dropbox/callback
        assert ("auth%2Fdropbox%2Fcallback" in location or "auth/dropbox/callback" in location)

    @pytest.mark.asyncio
    async def test_auth_url_includes_response_type_code(self, client: AsyncClient):
        """Test 4: Auth URL includes response_type=code"""
        response = await client.get("/auth/dropbox/login", follow_redirects=False)
        location = response.headers["location"]
        assert "response_type=code" in location


class TestOAuth2Callback:
    """Tests for OAuth2 callback and token exchange"""

    @pytest.mark.asyncio
    async def test_callback_exchanges_code_for_token(self, client: AsyncClient):
        """Test 5: Callback intercambia código por token"""
        # Mock Dropbox API response
        mock_token_response = {
            "access_token": "test_token_123",
            "token_type": "bearer",
            "account_id": "dbid:test123",
            "uid": "12345"
        }

        with patch("app.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            mock_exchange.return_value = mock_token_response

            response = await client.get(
                "/auth/dropbox/callback?code=test_auth_code",
                follow_redirects=False
            )

            # Should redirect to frontend
            assert response.status_code == 307
            # Should have called exchange function
            mock_exchange.assert_called_once_with("test_auth_code")

    @pytest.mark.asyncio
    async def test_callback_stores_token_in_session(self, client: AsyncClient):
        """Test 6: Callback almacena token en sesión"""
        mock_token_response = {
            "access_token": "stored_token_456",
            "account_id": "dbid:stored123"
        }

        with patch("app.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            mock_exchange.return_value = mock_token_response

            # Execute callback
            await client.get("/auth/dropbox/callback?code=test_code")

            # Check status endpoint shows authenticated
            status_response = await client.get("/auth/status")
            data = status_response.json()
            assert data["authenticated"] is True
            assert data["account_id"] == "dbid:stored123"


class TestAuthStatus:
    """Tests for auth status endpoint"""

    @pytest.mark.asyncio
    async def test_auth_status_returns_true_when_authenticated(self, client: AsyncClient):
        """Test 7: /auth/status retorna true si hay token"""
        # Simulate login
        mock_token_response = {
            "access_token": "valid_token",
            "account_id": "dbid:user123"
        }

        with patch("app.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            mock_exchange.return_value = mock_token_response

            await client.get("/auth/dropbox/callback?code=auth_code")

        # Check status
        response = await client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "account_id" in data

    @pytest.mark.asyncio
    async def test_auth_status_returns_false_when_not_authenticated(self, client: AsyncClient):
        """Test 8: /auth/status retorna false si no hay token"""
        # Clear any existing session first
        auth.clear_session()

        response = await client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data.get("account_id") is None


class TestLogout:
    """Tests for logout endpoint"""

    @pytest.mark.asyncio
    async def test_logout_removes_token(self, client: AsyncClient):
        """Test 9: /auth/logout elimina token"""
        # First login
        mock_token_response = {
            "access_token": "token_to_delete",
            "account_id": "dbid:user456"
        }

        with patch("app.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            mock_exchange.return_value = mock_token_response

            await client.get("/auth/dropbox/callback?code=code123")

        # Verify authenticated
        status1 = await client.get("/auth/status")
        assert status1.json()["authenticated"] is True

        # Logout
        logout_response = await client.post("/auth/logout")
        assert logout_response.status_code == 200
        assert logout_response.json()["success"] is True

        # Verify not authenticated
        status2 = await client.get("/auth/status")
        assert status2.json()["authenticated"] is False

    @pytest.mark.asyncio
    async def test_callback_fails_with_invalid_code(self, client: AsyncClient):
        """Test: Callback falla con código inválido"""
        with patch("app.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            mock_exchange.side_effect = HTTPException(status_code=400, detail="Invalid code")

            response = await client.get("/auth/dropbox/callback?code=invalid_code", follow_redirects=False)

            # Should redirect with error
            assert response.status_code == 307
            assert "auth_error" in response.headers["location"]
