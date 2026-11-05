import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("site", Path(__file__).with_name("prepare-site.py"))
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def build(files):
    root = Path(tempfile.mkdtemp())
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())
    return root


class PrepareSiteTests(unittest.TestCase):
    def test_copies_markdown_and_static_files_but_not_encrypted_or_github_files(self):
        root = build({
            "README.md": "# Accueil\n", "OS/Linux/x.md": "# X\n", ".github/workflows/README.md": "# CI\n",
            "OS/" + "a" * 32 + ".age": b"age-encryption.org/v1\n", "INDEX.json": "{}", "llms.txt": "# x\n",
            ".git/config": "[core]\n", "notes.txt": "texte",
        })
        destination = Path(tempfile.mkdtemp()) / "site-src"
        self.assertEqual(site.prepare(root, destination), 2)
        copied = sorted(p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file())
        self.assertEqual(copied, ["INDEX.json", "OS/Linux/x.md", "README.md", "llms.txt", "robots.txt"])

    def test_robots_blocks_indexing_by_default_and_can_be_opened(self):
        root = build({"README.md": "# A\n"})
        closed, opened = Path(tempfile.mkdtemp()) / "a", Path(tempfile.mkdtemp()) / "b"
        site.prepare(root, closed)
        site.prepare(root, opened, allow_indexing=True)
        self.assertIn("Disallow: /", (closed / "robots.txt").read_text())
        self.assertIn("Allow: /", (opened / "robots.txt").read_text())

    def test_symlinks_and_oversized_files_are_ignored(self):
        root = build({"README.md": "# A\n"})
        secret = root / "secret.txt"
        secret.write_text("SECRET")
        (root / "lien.md").symlink_to(secret)
        (root / "gros.md").write_bytes(b"# G\n" + b"x" * (site.MAX_BYTES + 1))
        destination = Path(tempfile.mkdtemp()) / "out"
        self.assertEqual(site.prepare(root, destination), 1)
        self.assertFalse((destination / "lien.md").exists())

    def test_links_to_repository_files_missing_from_the_site_point_to_github(self):
        root = build({
            "README.md": "# A\n\n[ci](.github/workflows/x.yml) [fiche](OS/x.md) [web](https://exemple.org/a) [haut](#titre)\n",
            "OS/x.md": "# X\n\n[patch](p.patch) [racine](../README.md#a) [absent](inexistant.md)\n",
            "OS/p.patch": "diff\n", ".github/workflows/x.yml": "name: x\n", "INDEX.json": "{}",
        })
        destination = Path(tempfile.mkdtemp()) / "out"
        site.prepare(root, destination)
        home = (destination / "README.md").read_text(encoding="utf-8")
        self.assertIn(site.BLOB + ".github/workflows/x.yml", home)
        self.assertIn("(OS/x.md)", home)
        self.assertIn("(https://exemple.org/a)", home)
        self.assertIn("(#titre)", home)
        page = (destination / "OS/x.md").read_text(encoding="utf-8")
        self.assertIn(site.BLOB + "OS/p.patch", page)
        self.assertIn("(../README.md#a)", page)
        self.assertIn("(inexistant.md)", page)

    def test_refuses_to_write_over_the_repository_root(self):
        root = build({"README.md": "# A\n"})
        with self.assertRaises(ValueError):
            site.prepare(root, root)


if __name__ == "__main__":
    unittest.main()
