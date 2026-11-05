import importlib.util
from pathlib import Path
import unittest
import subprocess
import tempfile

spec = importlib.util.spec_from_file_location("guard", Path(__file__).with_name("check-repository.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def test_opaque_age_objects_are_allowed_in_any_rubric(self):
        valid = "OS/Linux/arch/07-RESOLUTION/CLAVIER/" + "a" * 32 + ".age"
        self.assertIsNone(guard.check(valid, b"age-encryption.org/v1\n..."))
        self.assertIsNotNone(guard.check("OS/Linux/arch/03-CONFIGURATION/name.age", b"age-encryption.org/v1\n..."))
        self.assertIsNotNone(guard.check(valid, b"plain"))
        self.assertIsNone(guard.check("autre/" + "a" * 32 + ".age", b"age-encryption.org/v1\n..."))

    def test_cleartext_archives_and_private_key_material_are_rejected(self):
        self.assertIsNotNone(guard.check("archive.tar.gz", b"data"))
        self.assertIsNotNone(guard.check("x.txt", b"AGE-SECRET-KEY-1" + b"A" * 50))
        self.assertIsNotNone(guard.check("x.txt", b"-----BEGIN " + b"OPENSSH PRIVATE KEY-----"))

    def test_backup_data_is_always_encrypted_but_documentation_stays_readable(self):
        prefix = "OS/Windows/08-SAUVEGARDE/"
        self.assertIsNotNone(guard.check(prefix + "settings.json", b"{}"))
        self.assertIsNone(guard.check(prefix + "procedure.md", b"documentation"))
        self.assertIsNone(guard.check(prefix + "a" * 32 + ".age", b"age-encryption.org/v1\n..."))
        self.assertIsNone(guard.check("OS/Linux/arch/03-CONFIGURATION/exemple.json", b"{}"))

    def test_sensitive_names_local_env_and_symlinks_are_rejected(self):
        self.assertIsNotNone(guard.check("key_API.json", b"{}"))
        self.assertIsNotNone(guard.check(".env", b"anything"))
        self.assertIsNotNone(guard.check("link", b"", "120000"))
        self.assertIsNone(guard.check("README.md", b"documentation"))
        self.assertIsNone(guard.check(".env.example", b"example"))

    def test_index_is_checked_even_when_worktree_is_clean(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            path = root / "x.txt"
            path.write_bytes(b"AGE-SECRET-KEY-1" + b"A" * 50)
            subprocess.run(["git", "-C", str(root), "add", "x.txt"], check=True)
            path.write_text("clean worktree file")
            previous = guard.ROOT
            guard.ROOT = root
            try:
                entries = guard.files_in(root)
                self.assertEqual(len(entries), 1)
                self.assertIsNotNone(guard.check("x.txt", entries["x.txt"]))
            finally:
                guard.ROOT = previous


if __name__ == "__main__":
    unittest.main()
