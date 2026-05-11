import pytest
from unittest.mock import MagicMock
from modules.search.fofa_api import FoFa
from common.module_status import ModuleRunStatus
import requests

def test_error_status_mapping(mocker):
    fofa = FoFa('example.com')
    fofa.email = 'test'
    fofa.key = 'test'
    
    mock_get = mocker.patch('common.module.Module.get')
    
    # 401
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_get.return_value = mock_resp
    fofa.search()
    assert fofa.status == ModuleRunStatus.AUTH_FAILED
    
    # 402
    mock_resp.status_code = 402
    fofa.search()
    assert fofa.status == ModuleRunStatus.QUOTA_EXCEEDED

    # 403
    mock_resp.status_code = 403
    fofa.search()
    assert fofa.status == ModuleRunStatus.AUTH_FAILED
    
    # 429
    mock_resp.status_code = 429
    fofa.search()
    assert fofa.status == ModuleRunStatus.RATE_LIMITED
    
    # Network Error
    mock_get.return_value = None
    fofa.search()
    assert fofa.status == ModuleRunStatus.NETWORK_ERROR

def test_parse_error_mapping(mocker):
    fofa = FoFa('example.com')
    fofa.email = 'test'
    fofa.key = 'test'

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError('bad json')
    mocker.patch('common.module.Module.get', return_value=mock_resp)

    fofa.search()

    assert fofa.status == ModuleRunStatus.PARSE_ERROR
