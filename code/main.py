import typer
from pathlib import Path
from tree import FileBinaryTree

app = typer.Typer()
tree = FileBinaryTree()
FILES_DIR = Path("files")


@app.command()
def add(
        file_name: str,
        version: str,
        language: str,
        content: str = typer.Option("", help="Optional content for the .md file")
):
    """Add a file entry and generate the .md file automatically in a language folder."""
    language_dir = FILES_DIR / language.lower()
    language_dir.mkdir(parents=True, exist_ok=True)

    file_base_name = f"{file_name}_{version}.md"
    file_path = language_dir / file_base_name

    if file_path.exists():
        typer.echo(f"⚠️ File {file_path} already exists. Overwriting.")

    # Write content (even if it's empty)
    file_path.write_text(content)

    tree.insert(file_name, version, language, str(file_path))
    typer.echo(f"✅ Created and added {file_path}")


@app.command()
def search(file_name: str, version: str, language: str):
    """Search for a file in the tree."""
    result = tree.search(file_name, version, language)
    if result:
        typer.echo(f"🔍 Found: {result.file_name} {result.version} ({result.language})")
        typer.echo(f"📄 File path: {result.file_path}")
    else:
        typer.echo("❌ File not found.")


@app.command()
def list():
    """List all files in the tree (in order)."""
    all_items = tree.list_all()
    if not all_items:
        typer.echo("🌲 Tree is empty.")
    for f, v, l in all_items:
        typer.echo(f"- {f} {v} ({l})")


if __name__ == "__main__":
    app()
