cat > shared/evals/metrics.py <<'PY'
from __future__ import annotations

from typing import Any, Dict, Optional


def _get(d: Dict[str, Any], path: str) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def assert_equals(actual: Any, expected: Any, label: str) -> Optional[str]:
    if actual != expected:
        return f"{label}: expected {expected!r}, got {actual!r}"
    return None


def assert_min(actual: Any, min_value: float, label: str) -> Optional[str]:
    try:
        if float(actual) < float(min_value):
            return f"{label}: expected >= {min_value}, got {actual}"
    except Exception:
        return f"{label}: not comparable (actual={actual!r})"
    return None


def assert_max(actual: Any, max_value: float, label: str) -> Optional[str]:
    try:
        if float(actual) > float(max_value):
            return f"{label}: expected <= {max_value}, got {actual}"
    except Exception:
        return f"{label}: not comparable (actual={actual!r})"
    return None


def assert_range(actual: Any, lo: float, hi: float, label: str) -> Optional[str]:
    try:
        v = float(actual)
        if v < float(lo) or v > float(hi):
            return f"{label}: expected in [{lo}, {hi}], got {v}"
    except Exception:
        return f"{label}: not comparable (actual={actual!r})"
    return None


def assert_contains(haystack: Any, needle: str, label: str) -> Optional[str]:
    if haystack is None:
        return f"{label}: expected to contain {needle!r}, got None"

    # string
    if isinstance(haystack, str):
        if needle.lower() not in haystack.lower():
            return f"{label}: expected to contain {needle!r}, got {haystack!r}"
        return None

    # list/tuple
    if isinstance(haystack, (list, tuple)):
        joined = " ".join(str(x) for x in haystack)
        if needle.lower() not in joined.lower():
            return f"{label}: expected list to contain {needle!r}, got {list(haystack)!r}"
        return None

    # dict
    if isinstance(haystack, dict):
        joined = " ".join([str(k) + " " + str(v) for k, v in haystack.items()])
        if needle.lower() not in joined.lower():
            return f"{label}: expected dict to contain {needle!r}, got {haystack!r}"
        return None

    return f"{label}: unsupported type for contains (actual={type(haystack).__name__})"


def assert_empty_list(actual: Any, label: str) -> Optional[str]:
    if actual is None:
        return f"{label}: expected empty list, got None"
    if not isinstance(actual, list):
        return f"{label}: expected list, got {type(actual).__name__}"
    if len(actual) != 0:
        return f"{label}: expected empty list, got {actual!r}"
    return None


def assert_min_count(actual: Any, min_count: int, label: str) -> Optional[str]:
    if actual is None:
        return f"{label}: expected count >= {min_count}, got None"
    if not isinstance(actual, list):
        return f"{label}: expected list, got {type(actual).__name__}"
    if len(actual) < min_count:
        return f"{label}: expected count >= {min_count}, got {len(actual)}"
    return None
PY
