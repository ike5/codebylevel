import typer
from pathlib import Path
from sortedcontainers import SortedDict
import json
from packaging.version import Version

app = typer.Typer()

FILES_DIR = Path("files")
DATA_FILE = Path("docs_index.json")

# Nested structure: docs[language][version] = [file_path]
docs = SortedDict()


def load_data():
    if DATA_FILE.exists():
        with DATA_FILE.open() as f:
            raw = json.load(f)
            for lang, versions in raw.items():
                docs[lang] = SortedDict({Version(ver): files for ver, files in versions.items()})


def save_data():
    serializable = {
        lang: {str(ver): files for ver, files in versions.items()}
        for lang, versions in docs.items()
    }
    with DATA_FILE.open("w") as f:
        json.dump(serializable, f, indent=2)


load_data()


@app.command()
def add(
        file_name: str,
        version: str,
        language: str,
        content: str = typer.Option("", help="Optional content for the .md file"),
        author: str = typer.Option("", help="Optional author for the .md file"),
        level: str = typer.Option("A.0.0", help="Optional level for the .md file"),
        tags: str = typer.Option("@class", help="Optional tags for the .md file"),
):
    """Add a file entry and generate the .md file automatically in a language folder."""
    language_dir = FILES_DIR / language.lower()
    language_dir.mkdir(parents=True, exist_ok=True)

    file_base_name = f"{file_name}_{version}.doc.md"
    file_path = language_dir / file_base_name

    if file_path.exists():
        typer.echo(f"⚠️ File {file_path} already exists. Overwriting.")

    if not content:
        content = f"""---
title: {file_name}
language: {language}
version: {version}
since: {version}
deprecated: false
level: {level}
tags: [{tags}]
author: {author}
---

### @class {file_name}

Describe your class or module here.
"""

    file_path.write_text(content)

    vkey = Version(version)
    lang_dict = docs.setdefault(language.lower(), SortedDict())
    lang_dict.setdefault(vkey, []).append(str(file_path))

    save_data()
    typer.echo(f"✅ Created and added {file_path}")


@app.command()
def search(file_name: str, version: str, language: str):
    """Search for a file in the structure."""
    lang_data = docs.get(language.lower())
    if not lang_data:
        typer.echo("❌ Language not found.")
        return

    vkey = Version(version)
    file_list = lang_data.get(vkey, [])
    matches = [f for f in file_list if file_name in Path(f).stem]
    if matches:
        for match in matches:
            typer.echo(f"📄 {match}")
    else:
        typer.echo("❌ File not found.")


@app.command()
def list():
    """List all files in the structure."""
    if not docs:
        typer.echo("🌲 No files in index.")
        return
    for lang, versions in docs.items():
        for version, files in versions.items():
            for f in files:
                typer.echo(f"- {lang} {version}: {f}")


@app.command()
def search_range(language: str, max_version: str):
    """Search for all files in a language less than a given version."""
    lang_data = docs.get(language.lower())
    if not lang_data:
        typer.echo("❌ Language not found.")
        return

    vkey = Version(max_version)
    found = False
    for version in lang_data.irange(maximum=vkey, inclusive=(True, False)):
        for file_path in lang_data[version]:
            typer.echo(f"- {version}: {file_path}")
            found = True

    if not found:
        typer.echo(f"🔍 No files found in {language} below version {max_version}.")


if __name__ == "__main__":
    app()
