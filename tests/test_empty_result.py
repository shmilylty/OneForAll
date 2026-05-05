import pytest
from unittest.mock import MagicMock
from modules.search.fofa_api import FoFa
from common.module_status import ModuleRunStatus

def test_empty_result(mocker):
    fofa = FoFa('example.com')
    fofa.email = 'test'
    fofa.key = 'test'
    
    mock_get = mocker.patch('common.module.Module.get')
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "error": False,
        "mode": "extended",
        "size": 0,
        "results": []
    }
    mock_get.return_value = mock_resp
    
    fofa.search()
    
    assert fofa.status == ModuleRunStatus.EMPTY
