#!/usr/bin/env python3
"""Règles propres au dépôt : guides, noms, liens et données à chiffrer."""
import argparse
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "OS").is_dir() and (parent / "AGENTS.md").is_file())
RUBRICS = {
    "01-INSTALLATION", "02-SYSTEME", "03-CONFIGURATION", "04-LOGICIEL",
    "05-SCRIPT", "06-MAINTENANCE", "07-RESOLUTION", "08-SAUVEGARDE", "09-NOTE",
}
SCOPE_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")

OPAQUE = re.compile(r"[0-9a-f]{32}\.age\Z")
SENSITIVE_NAME = re.compile(r"(?i)(api[-_ ]?key|key[-_ ]?api|cl[eé][-_ ]?api|secret|password|credential|identity|private[-_ ]?key)")
PRIVATE_CONTENT = re.compile(
    rb"(?m)^(?:AGE-SECRET-KEY-1[0-9A-Z]+|-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----)"
)
RAW_ARCHIVES = (".tar", ".tar.gz", ".tgz", ".zip", ".7z", ".iso", ".img", ".vhd", ".vhdx", ".dmp")


def check(name, data, mode="100644"):
    path = Path(name)
    if mode == "120000":
        return "lien symbolique à contrôler"
    if name.endswith(".age"):
        if not OPAQUE.fullmatch(path.name):
            return "nom d'objet chiffré non opaque"
        if not data.startswith(b"age-encryption.org/v1\n"):
            return "format chiffré attendu"
        return None
    if "08-SAUVEGARDE" in path.parts and path.suffix.lower() != ".md":
        return "les données de sauvegarde doivent être chiffrées"
    if name.lower().endswith(RAW_ARCHIVES):
        return "archive en clair"
    if path.name.startswith(".env") and path.name != ".env.example":
        return "fichier local potentiellement confidentiel"
    if SENSITIVE_NAME.search(path.name) and path.suffix.lower() not in (".md", ".py"):
        return "nom de fichier potentiellement confidentiel"
    if PRIVATE_CONTENT.search(data):
        return "identité privée détectée"
    return None



def files_in(root, worktree=False):
    if worktree:
        return {p.relative_to(root).as_posix(): p.read_bytes()
                for p in root.rglob("*") if p.is_file() and not p.is_symlink()
                and not any(x in (".git", "__pycache__") for x in p.relative_to(root).parts)}
    result = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=root,
                            capture_output=True, check=True)
    files = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        header, name = record.split(b"\t", 1)
        mode, oid, stage = header.decode().split()
        if stage != "0" or mode == "120000":
            raise ValueError("Conflit ou lien symbolique non pris en charge.")
        content = subprocess.run(["git", "cat-file", "blob", oid], cwd=root,
                                 capture_output=True, check=True).stdout
        files[name.decode()] = content
    return files


def validate(files):
    errors = []
    directories = {PurePosixPath(".")}
    for name in files:
        directories.update(PurePosixPath(name).parents)
    for directory in directories:
        under_os = directory.parts and directory.parts[0] == "OS"
        guides = ("00-AGENTS.md", "README.md") if under_os else ("AGENTS.md", "README.md")
        for guide in guides:
            path = str(directory / guide)
            if path not in files:
                errors.append(f"Guide obligatoire absent : {path}")
            elif len(files[path].strip()) < 80 or not files[path].lstrip().startswith(b"# "):
                errors.append(f"Guide vide ou sans présentation : {path}")
        if directory == PurePosixPath("."):
            continue
        if directory.parts[0] not in ("OS", "OUTILS", ".github"):
            errors.append("Dossier racine non autorisé.")
            continue
        if not under_os:
            continue
        for obsolete in ("AGENTS.md", "00-README.md"):
            if str(directory / obsolete) in files:
                errors.append(f"Nom de guide obsolète sous OS : {directory}")
        if directory == PurePosixPath("OS"):
            if {p.name for p in directories if p.parent == directory} != {"Linux", "Windows"}:
                errors.append("OS doit séparer Linux et Windows.")
            continue
        if directory == PurePosixPath("OS/Linux"):
            if {p.name for p in directories if p.parent == directory} != {"arch", "ubuntu", "fedora", "debian"}:
                errors.append("Familles Linux attendues : arch, ubuntu, fedora, debian.")
            continue
        name = directory.name
        is_scope = directory == PurePosixPath("OS/Windows") or bool(SCOPE_NAME.fullmatch(name))
        if is_scope:
            children = {p.name for p in directories if p.parent == directory}
            if not RUBRICS.issubset(children):
                errors.append(f"Rubriques standard incomplètes : {directory}")
        elif name != name.upper() or (re.match(r"^\d+-", name) and name not in RUBRICS):
            errors.append(f"Nomenclature de rubrique ou catégorie invalide : {directory}")
    paths = set(files) | {str(p) for p in directories}
    for name, content in files.items():
        if not name.endswith(".md"):
            continue
        text = content.decode("utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            target = unquote(parsed.path)
            if not target:
                continue
            base = PurePosixPath(name).parent
            parts = []
            invalid = target.startswith("/")
            for part in (base / target).parts:
                if part == "..":
                    if not parts:
                        invalid = True
                        break
                    parts.pop()
                elif part != ".":
                    parts.append(part)
            if invalid or ("/".join(parts) or ".") not in paths:
                errors.append(f"Lien local invalide dans {name}")
        for target in re.findall(r"`((?:\.\./)+(?:00-)?AGENTS\.md)`", text):
            # Les chaînes de lecture ne sont pas toujours des liens Markdown.
            base = list(PurePosixPath(name).parent.parts)
            for part in PurePosixPath(target).parts:
                if part == ".." and base:
                    base.pop()
                else:
                    base.append(part)
            if "/".join(base) not in files:
                errors.append(f"Guide parent invalide dans {name}")
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", action="store_true")
    args = parser.parse_args()
    try:
        files = files_in(ROOT, args.worktree)
        errors = validate(files)
        errors.extend(sorted({reason for name, data in files.items()
                              if (reason := check(name, data)) is not None}))
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print(f"Structure, liens et politique des données valides : {len(files)} fichiers contrôlés.")
        return 0
    except (OSError, ValueError, UnicodeError, subprocess.CalledProcessError):
        print("Structure impossible à contrôler ; vérifier Git ou utiliser --worktree.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
