from modules.collect import Collect


def test_collect_filters_non_default_status_modules():
    collect = Collect("example.com")
    collect.get_mod()

    assert "modules.search.zoomeye_api" not in collect.modules
    assert "modules.search.bing_api" not in collect.modules
    assert "modules.search.google" not in collect.modules
