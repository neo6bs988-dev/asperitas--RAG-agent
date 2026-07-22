"""Prompt-harness evaluation controls for Asperitas.

These controls are public-safe development infrastructure. They do not
establish deployment, protected-holdout performance, scientific or legal
clearance, rights clearance, or production readiness.
"""

from .candidate_eval import compare_candidates
from .context_quality import evaluate_context
from .diagnostics import diagnose_failure_layer
from .release_gate import decide_release

__all__ = [
    "compare_candidates",
    "decide_release",
    "diagnose_failure_layer",
    "evaluate_context",
]

__version__ = "0.9.0"
