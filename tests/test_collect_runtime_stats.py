from common.module_status import record_module_run
from modules.collect import Collect


def test_collect_merges_runtime_module_status(mocker):
    collect = Collect("example.com")
    collect.modules = ["modules.search.fofa_api"]
    collect.collect_funcs = [[lambda domain: record_module_run("modules.search.fofa_api", "success", 2, "", 5), "fofa_api"]]

    collect.run()

    assert collect.module_results
    assert collect.module_results[0]["module_name"] == "modules.search.fofa_api"
    assert collect.module_results[0]["status"] == "success"
    assert collect.module_results[0]["count"] == 2
