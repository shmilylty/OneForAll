import pytest
from unittest.mock import patch, MagicMock
from modules.search.fofa_api import FoFa
from common.module_status import ModuleRunStatus

def test_fofa_parser(mocker):
    fofa = FoFa('example.com')
    fofa.email = 'test@example.com'
    fofa.key = 'testkey'
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "error": False,
        "mode": "extended",
        "size": 2,
        "results": [
            ["https://a.example.com", "1.1.1.1", "443", "https", "example.com", "Title A"],
            ["http://b.example.com", "2.2.2.2", "80", "http", "example.com", "Title B"]
        ]
    }
    
    mocker.patch('common.module.Module.get', return_value=mock_resp)
    
    fofa.search()
    
    assert fofa.status == ModuleRunStatus.SUCCESS
    assert 'a.example.com' in fofa.subdomains
    assert 'b.example.com' in fofa.subdomains
