from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_site import REQUIRED_FILES, validate_site  # noqa: E402


def copy_fixture(target: Path) -> None:
    for relative in REQUIRED_FILES:
        source = ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    key_file = next(
        path for path in ROOT.glob("*.txt")
        if len(path.stem) == 32 and all(ch in "0123456789abcdef" for ch in path.stem)
    )
    shutil.copy2(key_file, target / key_file.name)

    workflows = target / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        ROOT / ".github" / "workflows" / "indexnow.yml",
        workflows / "indexnow.yml",
    )


class SiteValidationTests(unittest.TestCase):
    def test_current_repository_is_valid(self) -> None:
        self.assertEqual(validate_site(ROOT), [])

    def test_wrong_cname_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            copy_fixture(fixture)
            (fixture / "CNAME").write_text("example.com\n", encoding="utf-8")
            self.assertTrue(any("CNAME" in error for error in validate_site(fixture)))

    def test_missing_local_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            copy_fixture(fixture)
            index = fixture / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8")
                .replace("site.js", "missing-script.js", 1),
                encoding="utf-8",
            )
            errors = validate_site(fixture)
            self.assertTrue(any("missing local HTML reference" in error for error in errors))

    def test_unpinned_action_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            copy_fixture(fixture)
            workflow = fixture / ".github" / "workflows" / "indexnow.yml"
            text = workflow.read_text(encoding="utf-8")
            text = text.replace(
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/checkout@v7",
            )
            workflow.write_text(text, encoding="utf-8")
            errors = validate_site(fixture)
            self.assertTrue(any("not pinned to a full SHA" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
