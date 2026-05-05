import pytest
from config import settings
from modules.collect import Collect

def test_default_module_config():
    assert getattr(settings, 'enable_all_module', False) is False
    assert getattr(settings, 'request_ssl_verify', True) is True

def test_deprecated_unstable_not_scheduled():
    collect = Collect('example.com')
    collect.get_mod()
    modules = collect.modules
    
    deprecated_modules = getattr(settings, 'deprecated_modules', [])
    unstable_modules = getattr(settings, 'unstable_modules', [])
    
    for mod in deprecated_modules:
        assert mod not in modules
    
    for mod in unstable_modules:
        assert mod not in modules

def test_recommended_modules_are_default_schedule():
    collect = Collect('example.com')
    collect.get_mod()
    assert collect.modules == getattr(settings, 'recommended_modules', [])

def test_module_status_mapping_contains_expected_classes():
    status_mapping = getattr(settings, 'module_status', None)
    if status_mapping is None:
        status_mapping = getattr(settings, 'module_status_mapping', {})

    assert status_mapping["modules.search.fofa_api"] == "stable"
    assert status_mapping["modules.search.zoomeye_api"] == "needs_migration"
    assert status_mapping["modules.datasets.cloudflare_api"] == "stable"
