import pytest
from unittest.mock import patch, MagicMock
from modules.search.hunter_api import Hunter
from common.module_status import ModuleRunStatus

def test_hunter_parser(mocker):
    hunter = Hunter('example.com')
    hunter.key = 'testkey'
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "code": 200,
        "message": "success",
        "data": {
            "arr": [
                {
                    "url": "https://a.example.com",
                    "ip": "1.1.1.1",
                    "port": 443,
                    "web_title": "Title A"
                },
                {
                    "domain": "b.example.com",
                    "ip": "2.2.2.2",
                    "port": 80,
                    "web_title": "Title B"
                }
            ],
            "total": 2
        }
    }
    
    mocker.patch('common.module.Module.get', return_value=mock_resp)
    
    hunter.search()
    
    assert hunter.status == ModuleRunStatus.SUCCESS
    assert 'a.example.com' in hunter.subdomains
    assert 'b.example.com' in hunter.subdomains
