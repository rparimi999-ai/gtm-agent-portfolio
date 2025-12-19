from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class EvalCase:
    id: str
    input: Dict[str, Any]
    expected: Dict[str, Any]
    notes: Optional[str] = None


@dataclass
class EvalResult:
    case_id: str
    passed: bool
    failures: List[str]
    debug: Dict[str, Any]
