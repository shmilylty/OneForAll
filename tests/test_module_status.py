from common.module import Module
from common.module_status import ModuleRunStatus


def test_module_initial_status_and_summary_shape():
    module = Module()

    assert module.status == "unknown"
    assert hasattr(module, "run_meta")
    assert module.run_meta["status"] == "unknown"
    assert module.run_meta["count"] == 0
    assert module.run_meta["error_message"] == ""


def test_module_can_record_explicit_status():
    module = Module()
    module.update_run_status(ModuleRunStatus.EMPTY, error_message="no data")

    assert module.status == ModuleRunStatus.EMPTY
    assert module.run_meta["status"] == ModuleRunStatus.EMPTY
    assert module.run_meta["error_message"] == "no data"
