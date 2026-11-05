import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("structure", Path(__file__).with_name("check-repository.py"))
structure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structure)


def fixture():
    files = {}
    description = b"# Guide\n\n" + b"Useful documentation about the purpose and maintenance of this directory. " * 2
    groups = ["", "OS", "OS/Linux", "OS/Windows", "OS/Linux/arch", "OS/Linux/ubuntu",
              "OS/Linux/fedora", "OS/Linux/debian"]
    scopes = ["OS/Windows", "OS/Linux/arch", "OS/Linux/ubuntu", "OS/Linux/fedora", "OS/Linux/debian"]
    groups += [scope + "/" + rubric for scope in scopes for rubric in structure.RUBRICS]
    for directory in groups:
        prefix = directory + "/" if directory else ""
        names = ("00-AGENTS.md", "README.md") if directory else ("AGENTS.md", "README.md")
        for name in names:
            files[prefix + name] = description
    return files


class StructureTests(unittest.TestCase):
    def test_valid_numbered_structure(self):
        self.assertEqual(structure.validate(fixture()), [])

    def test_missing_guide_rejects_a_directory(self):
        files = fixture()
        del files["OS/Linux/arch/00-AGENTS.md"]
        self.assertTrue(structure.validate(files))

    def test_unnumbered_guide_under_os_is_rejected(self):
        files = fixture()
        files["OS/Linux/arch/AGENTS.md"] = files["AGENTS.md"]
        self.assertTrue(structure.validate(files))

    def test_broken_local_link_is_rejected(self):
        files = fixture()
        files["README.md"] += b"\n[missing](OS/missing.md)\n"
        self.assertTrue(structure.validate(files))

    def test_technical_github_folder_requires_standard_guides(self):
        files = fixture()
        files[".github/workflows/example.yml"] = b"name: example"
        self.assertTrue(structure.validate(files))
        for directory in (".github", ".github/workflows"):
            for guide in ("AGENTS.md", "README.md"):
                files[directory + "/" + guide] = files[guide]
        self.assertEqual(structure.validate(files), [])

    def test_missing_rubric_rejects_scope(self):
        files = fixture()
        for name in list(files):
            if name.startswith("OS/Linux/arch/09-NOTE/"):
                del files[name]
        self.assertTrue(structure.validate(files))


if __name__ == "__main__":
    unittest.main()
