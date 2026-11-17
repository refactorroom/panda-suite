"""Reviewer-only correct control; never copy into task workspaces."""

from pathlib import Path


def decide(report, process_exit, timed_out):
    if timed_out or not isinstance(report, dict):
        return "INCONCLUSIVE"
    decision = report.get("decision")
    expected_exit = {"PASS": 0, "FAIL": 1}
    if not isinstance(decision, str) or decision not in expected_exit:
        return "INCONCLUSIVE"
    if type(process_exit) is not int or process_exit != expected_exit[decision]:
        return "INCONCLUSIVE"
    return decision


def evidence_path(root, relative):
    root = root.resolve()
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("unsafe evidence path")
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise ValueError("unsafe evidence path")
    return target
