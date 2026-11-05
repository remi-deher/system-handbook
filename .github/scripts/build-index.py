#!/usr/bin/env python3
"""Génère INDEX.json, INDEX.md et llms.txt à partir des fichiers Markdown du dépôt.

INDEX.json contient tous les fichiers .md (fiches, outils, portées, documents et guides). INDEX.md et
llms.txt restent limités aux fiches, outils, portées et documents généraux pour rester lisibles.

La source de vérité reste le texte des fiches : titre (premier `# `), lignes de métadonnées
(`Résumé :`, `Statut :`, `Date :`, `Portée :`) et chemin. Rien n'est saisi en double.

Usage :
    python -B .github/scripts/build-index.py          # écrit les fichiers ; code 1 s'ils ont changé
    python -B .github/scripts/build-index.py --check  # n'écrit rien ; code 1 si l'index est périmé

Le résultat est déterministe (aucune date, tri fixe, fins de ligne normalisées).

Sécurité : le script ne lit que des fichiers .md ordinaires. Les liens symboliques et les fichiers de plus de
512 Kio sont ignorés, car la CI l'exécute sur des fichiers d'une branche (option --root) avec des droits d'écriture.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "OS").is_dir() and (parent / "AGENTS.md").is_file())
REPO = "remi-deher/system-handbook"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
OUTPUTS = ("INDEX.json", "INDEX.md", "llms.txt")
GUIDES = {"README.md", "00-AGENTS.md", "AGENTS.md"}
GENERAL_DOCS = ("README.md", "AGENTS.md", "CONTRIBUTING.md", "CHIFFREMENT.md")
# Fichiers jamais indexés : les sorties elles-mêmes (sinon l'index dépend de lui-même) et le modèle de fiche.
SKIPPED = {"INDEX.md", "MODELE-FICHE.md"}
RUBRICS = {
    "01-INSTALLATION", "02-SYSTEME", "03-CONFIGURATION", "04-LOGICIEL",
    "05-SCRIPT", "06-MAINTENANCE", "07-RESOLUTION", "08-SAUVEGARDE", "09-NOTE",
}
METADATA = re.compile(
    r"^(?:[-*]\s+)?(Résumé|Statut|Date|Portée|Environnements testés|Prérequis et exclusions)\s*:\s*(.+?)\s*$")
MAX_SUMMARY = 280
MAX_BYTES = 512 * 1024


def clean(text):
    """Texte brut : liens réduits à leur libellé, gras et espaces superflus retirés."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip()


def first_sentence(text):
    """Première phrase, pour les résumés déduits du texte (un `Résumé :` explicite n'est pas coupé)."""
    found = re.search(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ`])", text)
    return text[:found.start()] if found else text


def truncate(text, limit=MAX_SUMMARY):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    stop = max(cut.rfind(". "), cut.rfind("; "))
    return (cut[:stop + 1] if stop > limit // 2 else cut.rsplit(" ", 1)[0] + "…").strip()


def parse(text):
    """Retourne (titre, métadonnées, résumé de repli) pour un document Markdown."""
    lines = text.replace("\r\n", "\n").split("\n")
    title, index = "", 0
    for index, line in enumerate(lines):
        if line.startswith("# "):
            title = clean(line[2:])
            break
    meta = {}
    paragraph, in_code = [], False
    for line in lines[index + 1:]:
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        found = METADATA.match(line)
        if found:
            meta.setdefault(found.group(1), clean(found.group(2)))
            continue
        if line.startswith("## ") and paragraph:
            break
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith((">", "|", "-", "*", "#", "<", "!", "[", "1.")):
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    return title, meta, truncate(first_sentence(clean(" ".join(paragraph))))


def classify(path):
    """Déduit os, famille, portées, rubrique et catégorie du chemin relatif."""
    parts = PurePosixPath(path).parts
    info = {"os": None, "family": None, "scopes": [], "rubric": None, "category": None}
    if parts[0] != "OS" or len(parts) < 3:
        return info
    info["os"] = parts[1]
    rest = list(parts[2:-1])
    if parts[1] == "Linux" and rest:
        info["family"] = rest.pop(0)
    scopes = []
    while rest and rest[0] not in RUBRICS and rest[0] == rest[0].lower():
        scopes.append(rest.pop(0))
    info["scopes"] = scopes
    if rest and rest[0] in RUBRICS:
        info["rubric"] = rest.pop(0)
        if rest:
            info["category"] = "/".join(rest)
    return info


def kind_of(path, info, is_scope):
    parts = PurePosixPath(path).parts
    if is_scope:
        return "scope"
    if PurePosixPath(path).name in GUIDES and len(parts) > 1:
        return "guide"
    if parts[0] == "OUTILS":
        return "tool"
    if parts[0] == "OS":
        return "fiche"
    return "doc"


def tags(info):
    values = [v for v in (info["os"], info["family"]) if v] + info["scopes"]
    if info["rubric"]:
        values.append(info["rubric"].split("-", 1)[1].lower())
    if info["category"]:
        values.extend(part.lower() for part in info["category"].split("/"))
    seen, out = set(), []
    for value in values:
        if value.lower() not in seen:
            seen.add(value.lower())
            out.append(value.lower())
    return out


def collect(root):
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md")
                   if ".git" not in p.relative_to(root).parts
                   and p.is_file() and not p.is_symlink() and p.stat().st_size <= MAX_BYTES)
    directories = {PurePosixPath(f).parent for f in files}
    scope_dirs = set()
    for directory in directories:
        parts = directory.parts
        if directory == PurePosixPath("OS/Windows"):
            scope_dirs.add(str(directory))
        elif len(parts) >= 3 and parts[:2] == ("OS", "Linux") and (root / directory / "07-RESOLUTION").is_dir():
            scope_dirs.add(str(directory))
    entries, errors = [], []
    for path in files:
        name = PurePosixPath(path).name
        parent = str(PurePosixPath(path).parent)
        is_scope = name == "README.md" and parent in scope_dirs
        if path in SKIPPED:
            continue
        title, meta, fallback = parse((root / path).read_text(encoding="utf-8"))
        info = classify(path)
        kind = kind_of(path, info, is_scope)
        summary = meta.get("Résumé") or fallback
        if kind in ("fiche", "tool") and "Résumé" not in meta:
            errors.append(f"Ligne « Résumé : … » manquante dans {path}")
        if not title:
            errors.append(f"Titre « # » manquant dans {path}")
        entry = {"path": path, "kind": kind, "title": title, "summary": summary}
        for key, field in (("Statut", "status"), ("Date", "date"), ("Portée", "scope_note")):
            if key in meta:
                entry[field] = meta[key].rstrip(".")
        entry.update({k: v for k, v in info.items() if v})
        entry["tags"] = tags(info)
        entries.append(entry)
    return entries, errors


def render_json(entries):
    return json.dumps({"version": 1, "repository": REPO, "entries": entries},
                      ensure_ascii=False, indent=2) + "\n"


def link(path):
    return f"[{path}]({path})"


def render_markdown(entries):
    out = ["# Index du dépôt", "",
           "Index généré automatiquement à partir des fiches : ne pas modifier à la main. "
           "Chaque ligne reprend le titre, le résumé et les métadonnées de la fiche. "
           "Version lisible par machine : [INDEX.json](INDEX.json). Navigation par dossiers : [README.md](README.md).", ""]
    groups = [("Portées", "scope"), ("Fiches", "fiche"), ("Outils communs", "tool"), ("Documents généraux", "doc")]
    for heading, kind in groups:
        rows = [e for e in entries if e["kind"] == kind]
        if not rows:
            continue
        out += [f"## {heading}", ""]
        for e in rows:
            extra = []
            if e.get("status"):
                extra.append(f"statut : {e['status']}")
            if e.get("date"):
                extra.append(f"date : {e['date']}")
            line = f"- **[{e['title']}]({e['path']})** — {e['summary']}"
            if extra:
                line += f" ({' ; '.join(extra)})"
            out.append(line)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_llms(entries):
    out = ["# System Handbook", "",
           "> Notes, résolutions, configurations et outils personnels pour Linux (Arch, Ryoku, Niri, Hyprland) "
           "et Windows. Contenu en français. Les données sensibles sont chiffrées avec age (fichiers `.age` à noms opaques) ; "
           "ne jamais demander ni afficher de clé privée.", "",
           "Lire d'abord AGENTS.md, puis les 00-AGENTS.md de la branche concernée. L'index complet, avec résumés et "
           "métadonnées, est INDEX.json.", ""]
    groups = [("Fiches", "fiche"), ("Outils communs", "tool"), ("Portées", "scope"), ("Documents généraux", "doc")]
    for heading, kind in groups:
        rows = [e for e in entries if e["kind"] == kind]
        if not rows:
            continue
        out += [f"## {heading}", ""]
        for e in rows:
            out.append(f"- [{e['title']}]({RAW}{e['path']}): {e['summary']}")
        out.append("")
    out += ["## Index", "", f"- [INDEX.json]({RAW}INDEX.json): index structuré de toutes les fiches",
            f"- [INDEX.md]({RAW}INDEX.md): index lisible", ""]
    return "\n".join(out).rstrip() + "\n"


def normalized(data):
    return data.replace(b"\r\n", b"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="ne rien écrire ; échouer si l'index est périmé")
    parser.add_argument("--root", type=Path, default=ROOT, help="racine à indexer (défaut : ce dépôt)")
    args = parser.parse_args()
    root = args.root.resolve()
    entries, errors = collect(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    rendered = {"INDEX.json": render_json(entries), "INDEX.md": render_markdown(entries),
                "llms.txt": render_llms(entries)}
    stale = []
    for name in OUTPUTS:
        target = root / name
        wanted = rendered[name].encode("utf-8")
        current = normalized(target.read_bytes()) if target.is_file() else None
        if target.is_symlink():
            print(f"Sortie refusée : {name} est un lien symbolique.", file=sys.stderr)
            return 2
        if current != wanted:
            stale.append(name)
            if not args.check:
                target.write_bytes(wanted)
    if stale:
        verb = "périmé" if args.check else "régénéré"
        print(f"Index {verb} : {', '.join(stale)}. Relancer pre-commit et ajouter ces fichiers.", file=sys.stderr)
        return 1
    print(f"Index à jour : {len(entries)} entrées.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
