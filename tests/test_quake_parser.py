import pytest
from unittest.mock import patch, MagicMock
from modules.search.quake_api import Quake
from common.module_status import ModuleRunStatus

def test_quake_parser(mocker):
    quake = Quake('example.com')
    quake.key = 'testkey'
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "code": 0,
        "data": [
            {
                "ip": "1.1.1.1",
                "port": 443,
                "service": {
                    "http": {
                        "host": "a.example.com",
                        "title": "Title A"
                    },
                    "tls": {
                        "cert": {
                            "subject": {
                                "cn": "b.example.com"
                            },
                            "subject_alt_names": [
                                "c.example.com",
                                "*.d.example.com"
                            ]
                        }
                    }
                }
            }
        ],
        "meta": {"pagination": {"total": 1}}
    }
    
    mocker.patch('common.module.Module.post', return_value=mock_resp)
    
    quake.search()
    
    assert quake.status == ModuleRunStatus.SUCCESS
    assert 'a.example.com' in quake.subdomains
    assert 'b.example.com' in quake.subdomains
    assert 'c.example.com' in quake.subdomains
    assert 'd.example.com' in quake.subdomains
