import importlib.machinery
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


loader = importlib.machinery.SourceFileLoader("clay_search", str(Path(__file__).with_name("clay-search")))
spec = importlib.util.spec_from_loader(loader.name, loader)
helper = importlib.util.module_from_spec(spec)
loader.exec_module(helper)


class CloudContentsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(shutil.which("rg"), "The regression checks need real ripgrep")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / ".git").mkdir()

    def file(self, name, contents="launchfixture\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path

    def matches(self, targets):
        return sorted(hit["path"] for hit in json.loads(helper.search(
            self.root, [], targets, "launchfixture", "contents", ()
        ))["value"]["matches"])

    def test_cloud_candidates_obey_the_same_ignore_rules_as_normal_search(self):
        self.file(".gitignore", "ignored.txt\nignored-folder/\n")
        self.file("visible.txt")
        self.file("line\nbreak.txt")
        self.file("ignored.txt")
        self.file("ignored-folder/inside.txt")
        self.file(".hidden.txt")
        self.file(".hidden-folder/inside.txt")
        targets, skipped = helper.local_files(self.root)
        expected = ["line\nbreak.txt", "visible.txt"]
        self.assertEqual(self.matches([str(self.root)]), expected)
        self.assertEqual(self.matches(targets), expected)
        self.assertEqual(skipped, 0)

    def test_placeholder_is_not_passed_to_content_search(self):
        placeholder = self.file("not-downloaded.txt")
        self.file("downloaded.txt")
        original = helper.os.lstat

        def lstat(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            if Path(path) == placeholder:
                return SimpleNamespace(st_mode=info.st_mode, st_flags=helper.SF_DATALESS)
            return info

        with patch.object(helper.os, "lstat", side_effect=lstat):
            targets, skipped = helper.local_files(self.root)
        self.assertEqual(targets, [str(self.root / "downloaded.txt")])
        self.assertEqual(skipped, 1)
        self.assertEqual(self.matches(targets), ["downloaded.txt"])

    def test_scope_exclusions_apply_before_candidate_limits(self):
        self.file("excluded/one.txt")
        self.file("excluded/two.txt")
        self.file("visible.txt")
        with patch.object(helper, "LOCAL_LIST_COUNT", 1):
            targets, skipped = helper.local_files(self.root, ["excluded"])
        self.assertEqual(targets, [str(self.root / "visible.txt")])
        self.assertEqual(skipped, 0)

    def test_empty_folder_and_candidate_cap(self):
        self.assertEqual(helper.local_files(self.root), ([], 0))
        for name in ["one.txt", "two.txt", "three.txt"]:
            self.file(name)
        with patch.object(helper, "LOCAL_LIST_COUNT", 1):
            targets, skipped = helper.local_files(self.root)
        self.assertEqual(len(targets), 1)
        self.assertEqual(skipped, 2)
        self.assertEqual(len(self.matches(targets)), 1)


if __name__ == "__main__":
    unittest.main()
