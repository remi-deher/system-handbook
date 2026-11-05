#!/usr/bin/env python3
"""Prépare le dossier source du site GitHub Pages à partir des fichiers Markdown du dépôt.

Copie tous les .md ordinaires (hors .git et .github), INDEX.json et llms.txt, puis écrit un robots.txt qui
demande aux moteurs de ne pas indexer le site (--allow-indexing pour l'autoriser). Les liens symboliques et
les fichiers de plus de 512 Kio sont ignorés. Aucun objet chiffré (.age) n'est copié.

Usage : python -B .github/scripts/prepare-site.py DESTINATION [--allow-indexing]
"""
import argparse
from pathlib import Path
import posixpath
import re
import shutil
import sys
from urllib.parse import unquote

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "OS").is_dir() and (parent / "AGENTS.md").is_file())
MAX_BYTES = 512 * 1024
STATIC = ("INDEX.json", "llms.txt")
ROBOTS = "User-agent: *\nDisallow: /\n"
ROBOTS_OPEN = "User-agent: *\nAllow: /\n"
BLOB = "https://github.com/remi-deher/system-handbook/blob/main/"
LINK = re.compile(r"(\]\()([^)\s]+)(\))")
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def sources(root, destination):
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if relative.parts[0] in (".git", ".github") or destination in path.parents:
            continue
        if path.is_file() and not path.is_symlink() and path.stat().st_size <= MAX_BYTES:
            yield relative


def rewrite_links(text, relative, root, published):
    """Les liens vers un fichier du dépôt absent du site pointent vers sa page sur GitHub."""
    base = posixpath.dirname(relative.as_posix())

    def fix(match):
        target = match.group(2)
        if SCHEME.match(target) or target.startswith(("#", "/")):
            return match.group(0)
        path, separator, fragment = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(base, unquote(path))) if path else ""
        if not path or resolved.startswith("..") or resolved in published:
            return match.group(0)
        candidate = root / resolved
        if candidate.is_file() and not candidate.is_symlink():
            return match.group(1) + BLOB + resolved + separator + fragment + match.group(3)
        return match.group(0)

    return LINK.sub(fix, text)


def prepare(root, destination, allow_indexing=False):
    root, destination = root.resolve(), destination.resolve()
    if destination == root or destination in root.parents:
        raise ValueError("La destination ne peut pas être la racine du dépôt ni l'un de ses parents.")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("La destination doit être vide ou inexistante : " + str(destination))
    destination.mkdir(parents=True, exist_ok=True)
    files = list(sources(root, destination))
    published = {relative.as_posix() for relative in files} | set(STATIC)
    count = 0
    for relative in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = (root / relative).read_text(encoding="utf-8")
        target.write_text(rewrite_links(text, relative, root, published), encoding="utf-8", newline="\n")
        count += 1
    for name in STATIC:
        source = root / name
        if source.is_file() and not source.is_symlink():
            shutil.copyfile(source, destination / name)
    (destination / "robots.txt").write_text(ROBOTS_OPEN if allow_indexing else ROBOTS, encoding="utf-8", newline="\n")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--allow-indexing", action="store_true")
    args = parser.parse_args()
    try:
        count = prepare(ROOT, args.destination, args.allow_indexing)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    print(f"Source du site prête : {count} fichiers Markdown.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
