import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("index", Path(__file__).with_name("build-index.py"))
index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(index)

FICHE = """# Titre de la fiche

- Résumé : Une phrase explicite, reprise telle quelle. Une seconde phrase aussi.
- Statut : **résolu**.
- Date : 2026-11-05.

## Diagnostic

Texte.
"""


class ParseTests(unittest.TestCase):
    def test_explicit_summary_and_metadata_are_read_without_markup(self):
        title, meta, _ = index.parse(FICHE)
        self.assertEqual(title, "Titre de la fiche")
        self.assertEqual(meta["Résumé"], "Une phrase explicite, reprise telle quelle. Une seconde phrase aussi.")
        self.assertEqual(meta["Statut"], "résolu.")
        self.assertEqual(meta["Date"], "2026-11-05.")

    def test_fallback_is_first_sentence_of_first_paragraph_and_skips_badges_and_tables(self):
        text = "# T\n\n[![Badge](a.svg)](b)\n\n| a | b |\n| - | - |\n\nPremière phrase. Deuxième phrase.\n\n## Suite\n"
        self.assertEqual(index.parse(text)[2], "Première phrase.")

    def test_crlf_gives_the_same_result_as_lf(self):
        self.assertEqual(index.parse(FICHE), index.parse(FICHE.replace("\n", "\r\n")))

    def test_code_blocks_never_become_summaries(self):
        text = "# T\n\n```bash\nStatut : faux\necho non\n```\n\nVrai texte.\n"
        _, meta, summary = index.parse(text)
        self.assertEqual(summary, "Vrai texte.")
        self.assertNotIn("Statut", meta)

    def test_long_summary_is_cut_on_a_boundary(self):
        text = "# T\n\n" + "mot " * 200 + "\n"
        self.assertLessEqual(len(index.parse(text)[2]), index.MAX_SUMMARY + 1)


class ClassifyTests(unittest.TestCase):
    def test_scope_rubric_and_category_come_from_the_path(self):
        info = index.classify("OS/Linux/arch/ryoku/niri/07-RESOLUTION/CLAVIER/x.md")
        self.assertEqual((info["os"], info["family"], info["scopes"], info["rubric"], info["category"]),
                         ("Linux", "arch", ["ryoku", "niri"], "07-RESOLUTION", "CLAVIER"))
        self.assertEqual(index.tags(info), ["linux", "arch", "ryoku", "niri", "resolution", "clavier"])

    def test_windows_has_no_family(self):
        info = index.classify("OS/Windows/03-CONFIGURATION/x.md")
        self.assertIsNone(info["family"])
        self.assertEqual(info["rubric"], "03-CONFIGURATION")


class CollectTests(unittest.TestCase):
    def build(self, files):
        root = Path(tempfile.mkdtemp())
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def test_fiche_without_summary_line_is_an_error(self):
        root = self.build({"OS/Windows/07-RESOLUTION/x.md": "# Sans résumé\n\nTexte.\n"})
        entries, errors = index.collect(root)
        self.assertEqual(len(entries), 1)
        self.assertTrue(any("Résumé" in error for error in errors))

    def test_guides_are_in_the_json_but_not_in_the_readable_outputs(self):
        root = self.build({
            "OS/Windows/07-RESOLUTION/fiche.md": FICHE,
            "OS/Windows/07-RESOLUTION/README.md": "# Guide\n\nTexte du guide.\n",
            "OS/Windows/07-RESOLUTION/00-AGENTS.md": "# Guide IA\n\nTexte IA.\n",
        })
        entries, errors = index.collect(root)
        self.assertEqual(errors, [])
        kinds = {e["path"]: e["kind"] for e in entries}
        self.assertEqual(kinds["OS/Windows/07-RESOLUTION/README.md"], "guide")
        self.assertEqual(kinds["OS/Windows/07-RESOLUTION/00-AGENTS.md"], "guide")
        for guide in ("OS/Windows/07-RESOLUTION/README.md", "OS/Windows/07-RESOLUTION/00-AGENTS.md"):
            self.assertNotIn(guide, index.render_markdown(entries))
            self.assertNotIn(guide, index.render_llms(entries))

    def test_generated_outputs_and_template_are_not_indexed(self):
        root = self.build({
            "OS/Windows/07-RESOLUTION/fiche.md": FICHE,
            "INDEX.md": "# Index\n\nTexte.\n",
            "MODELE-FICHE.md": "# Modèle\n\n- Résumé : x\n",
        })
        entries, errors = index.collect(root)
        self.assertEqual(errors, [])
        self.assertEqual([e["path"] for e in entries], ["OS/Windows/07-RESOLUTION/fiche.md"])

    def test_symlinked_and_oversized_markdown_files_are_ignored(self):
        root = self.build({"OS/Windows/07-RESOLUTION/fiche.md": FICHE})
        secret = root / "secret.txt"
        secret.write_text("SECRET-A-NE-JAMAIS-INDEXER\n", encoding="utf-8")
        (root / "OS/Windows/07-RESOLUTION/lien.md").symlink_to(secret)
        (root / "OS/Windows/07-RESOLUTION/gros.md").write_text("# Gros\n\n" + "x" * (index.MAX_BYTES + 1), encoding="utf-8")
        entries, errors = index.collect(root)
        self.assertEqual(errors, [])
        self.assertEqual([e["path"] for e in entries], ["OS/Windows/07-RESOLUTION/fiche.md"])
        self.assertNotIn("SECRET-A-NE-JAMAIS-INDEXER", index.render_json(entries))

    def test_rendering_is_deterministic(self):
        entries, _ = index.collect(index.ROOT)
        self.assertEqual(index.render_json(entries), index.render_json(entries))
        self.assertEqual(index.render_markdown(entries), index.render_markdown(entries))


class RepositoryTests(unittest.TestCase):
    def test_documents_produce_a_valid_index(self):
        # La fraîcheur des fichiers générés n'est pas contrôlée ici : la CI les met à jour sur chaque PR.
        # En revanche, une fiche sans « Résumé : » ou sans titre doit bloquer la fusion.
        entries, errors = index.collect(index.ROOT)
        self.assertEqual(errors, [])
        self.assertGreater(len(entries), 0)
        for render in (index.render_json, index.render_markdown, index.render_llms):
            self.assertTrue(render(entries).endswith("\n"))

    def test_generated_files_never_contain_private_key_material(self):
        for name in index.OUTPUTS:
            self.assertNotIn(b"AGE-SECRET-KEY-1", (index.ROOT / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
