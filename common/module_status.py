# coding=utf-8
class ModuleRunStatus:
    SUCCESS = "success"
    EMPTY = "empty"
    SKIPPED = "skipped"
    AUTH_FAILED = "auth_failed"
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMITED = "rate_limited"
    DEPRECATED = "deprecated"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PARSE_ERROR = "parse_error"
    NETWORK_ERROR = "network_error"


_MODULE_RUN_RECORDS = {}


def reset_module_run_records():
    _MODULE_RUN_RECORDS.clear()


def record_module_run(module_name, status, count=0, error_message="", elapsed_ms=0):
    _MODULE_RUN_RECORDS[module_name] = {
        "module_name": module_name,
        "status": status,
        "count": count,
        "error_message": error_message,
        "elapsed_ms": elapsed_ms,
    }


def get_module_run_records():
    return dict(_MODULE_RUN_RECORDS)
