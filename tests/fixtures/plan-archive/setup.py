"""Create an isolated plan-lifecycle task repository (no reviewer expectations)."""
import argparse
from pathlib import Path


def setup(destination, scenario):
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "service.py").write_text(
        'def slug(text):\n    return text.strip().lower().replace(" ", "-")\n')
    (destination / "test_service.py").write_text(
        'import unittest\nfrom service import slug\n\n'
        'class SlugTest(unittest.TestCase):\n'
        '    def test_basic(self):\n        self.assertEqual(slug("Hello World"), "hello-world")\n')
    folder = "design" if scenario == "custom" else ".panda-suite/plans"
    plans = destination / folder
    plans.mkdir(parents=True)
    complete = (
        '# Slug plan\n\nGoal: normalize a label into a slug.\n\n'
        '## Tasks\n\n- [x] T1: implement slug(text) in service.py; trim outer whitespace, '
        'lowercase and replace spaces with hyphens.\n'
        '  Acceptance: slug(" Hello World ") == "hello-world".\n'
        '  Verification: python3 -m unittest -v; also run the acceptance example directly.\n\n'
        '## Evidence\n\nPrior session reported both checks passed. Recheck current source.\n\n'
        '## Deviations\n\nNone.\n')
    if scenario in {"partial", "superseded", "ambiguous"}:
        complete += '\n- [ ] T2: add a usage.md example and run it.\n'
    if scenario == "stale":
        (destination / "service.py").write_text(
            'def slug(text):\n    return text.lower().replace(" ", "-")\n')
    (plans / "2026-11-15-slug.md").write_text(complete)
    if scenario in {"superseded", "ambiguous"}:
        (plans / "2026-11-16-slug-v2.md").write_text(
            '# Slug v2 proposal\n\n- [ ] T1: agree Unicode normalization policy.\n')
    (plans / "2026-11-16-pending.md").write_text(
        '# Pending plan\n\n- [ ] Add duplicate detection; policy unresolved.\n')
    (destination / ".gitignore").write_text('/.panda-suite/\n')
    if scenario == "collision":
        (plans / "archive").mkdir()
        (plans / "archive/2026-11-15-slug.md").write_text('# Older archived plan\n')
    if scenario == "failure":
        (plans / "archive").write_text('Existing user file; keep it.\n')
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=["complete", "partial", "stale", "collision",
                                             "failure", "readonly", "custom",
                                             "superseded", "ambiguous"])
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(setup(args.destination, args.scenario))
