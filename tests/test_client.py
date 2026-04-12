import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError, ConnectionError
from client import WalletClient


@pytest.fixture
def client():
    return WalletClient(api_token="test-token", api_url="https://api.example.com")


def make_response(data: dict, status_code: int = 200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    mock.json.return_value = data
    return mock


def test_returns_records_single_page(client):
    expected = [{"id": "1"}, {"id": "2"}]
    with patch("client.get", return_value=make_response({"records": expected})):
        result = client.get_records_in_range("2026-04-01", "2026-04-12")
    assert result == expected


def test_pagination_fetches_all_pages(client):
    page1 = make_response({"records": [{"id": "1"}], "nextOffset": "200"})
    page2 = make_response({"records": [{"id": "2"}]})
    with patch("client.get", side_effect=[page1, page2]) as mock_get:
        result = client.get_records_in_range("2026-04-01", "2026-04-12")

    assert result == [{"id": "1"}, {"id": "2"}]
    assert mock_get.call_count == 2
    second_call_params = mock_get.call_args_list[1].kwargs["params"]
    assert second_call_params["offset"] == "200"


def test_raises_on_http_error(client):
    mock_response = make_response({}, status_code=401)
    mock_response.raise_for_status.side_effect = HTTPError("401 Unauthorized")
    with patch("client.get", return_value=mock_response):
        with pytest.raises(HTTPError):
            client.get_records_in_range("2026-04-01", "2026-04-12")


def test_raises_on_missing_records_key(client):
    with patch("client.get", return_value=make_response({"error": "unexpected"})):
        with pytest.raises(ValueError, match="'records' key missing"):
            client.get_records_in_range("2026-04-01", "2026-04-12")


def test_raises_on_network_error(client):
    with patch("client.get", side_effect=ConnectionError("connection refused")):
        with pytest.raises(ConnectionError):
            client.get_records_in_range("2026-04-01", "2026-04-12")
