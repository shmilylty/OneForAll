import pytest
from unittest.mock import MagicMock
from modules.datasets.cloudflare_api import CloudFlareAPI

def test_cloudflare_safety(mocker):
    cf = CloudFlareAPI('example.com')
    cf.token = 'testtoken'
    
    # Mock get to return empty zone list
    mock_get = mocker.patch('common.module.Module.get')
    mock_resp_acc = MagicMock()
    mock_resp_acc.status_code = 200
    mock_resp_acc.json.return_value = {"result": [{"id": "acc123"}]}
    
    mock_resp_zone = MagicMock()
    mock_resp_zone.status_code = 200
    mock_resp_zone.json.return_value = {"success": True, "result": []} # empty zone
    
    mock_get.side_effect = [mock_resp_acc, mock_resp_zone]
    
    mock_post = mocker.patch('common.module.Module.post')
    
    cf.query()
    
    # Assert post was never called
    mock_post.assert_not_called()

def test_cloudflare_existing_zone_only_lists_dns(mocker):
    cf = CloudFlareAPI('example.com')
    cf.token = 'testtoken'

    mock_get = mocker.patch('common.module.Module.get')
    mock_post = mocker.patch('common.module.Module.post')

    mock_resp_acc = MagicMock()
    mock_resp_acc.status_code = 200
    mock_resp_acc.json.return_value = {"result": [{"id": "acc123"}]}

    mock_resp_zone = MagicMock()
    mock_resp_zone.status_code = 200
    mock_resp_zone.json.return_value = {"success": True, "result": [{"id": "zone123"}]}

    mock_resp_dns = MagicMock()
    mock_resp_dns.status_code = 200
    mock_resp_dns.text = "api.example.com cdn.example.com"
    mock_resp_dns.json.return_value = {"result_info": {"total_pages": 1}}

    mock_get.side_effect = [mock_resp_acc, mock_resp_zone, mock_resp_dns, mock_resp_dns]

    cf.query()

    mock_post.assert_not_called()
    assert "api.example.com" in cf.subdomains
