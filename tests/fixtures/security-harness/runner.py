"""Synthetic local harness functions; no subprocesses or network access."""


def decide(report, process_exit, timed_out):
    """Return the provider decision for the required gate."""
    return report["decision"]


def evidence_path(root, relative):
    """Locate provider-named evidence under the approved evidence root."""
    return root / relative
