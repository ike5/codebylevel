from typing import List
from pathlib import Path
import json
import hashlib
import subprocess
import typer
from rich.console import Console
from git import Repo
from datetime import datetime
import re
import tempfile
import os
from packaging.version import parse as parse_version
from rapidfuzz import fuzz

METADATA_TAXONOMY_PATH = Path("metadata_taxonomy.json")

app = typer.Typer()
console = Console()
DOCS_DIR = Path("docs_by_level")


def load_taxonomy():
    if METADATA_TAXONOMY_PATH.exists():
        with open(METADATA_TAXONOMY_PATH, "r") as f:
            return json.load(f)
    else:
        return {}


def select_metadata_path(taxonomy: dict) -> str:
    current = taxonomy
    path_parts = []

    while isinstance(current, dict) and current:
        keys = list(current.keys())
        console.print(f"\n[bold blue]Options:[/bold blue] {', '.join(keys)}")
        choice = typer.prompt("Choose one")
        if choice not in current:
            console.print(f"[red]Invalid choice:[/red] {choice}. Please choose from: {keys}")
            continue
        path_parts.append(choice)
        current = current[choice]

    return ".".join(path_parts)


@app.command()
def select_metadata(
        key: str = typer.Option(..., help="Metadata key path to select")
):
    console.print(f"[green]Selected metadata key:[/green] {key}")


def get_multiline_input_from_editor() -> str:
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tf_path = tf.name
    editor = os.environ.get("EDITOR", "vi")
    subprocess.call([editor, tf_path])
    with open(tf_path, "r") as f:
        content = f.read()
    os.unlink(tf_path)
    return content


def hash_doc(doc: dict) -> str:
    raw = json.dumps(doc, sort_keys=True).encode()
    return hashlib.sha1(raw).hexdigest()


def matches_title(doc_title, search_title):
    doc_title = doc_title.lower()
    search_title = search_title.lower()
    score = fuzz.partial_ratio(doc_title, search_title)
    return score > 60


@app.command()
def add():
    console.rule("[bold blue]Add Documentation[/bold blue]")

    supported_languages = ["python", "swift", "javascript", "java", "c++"]
    while True:
        language = typer.prompt("Programming language")
        if language.lower() in supported_languages:
            break
        console.print(f"[red]Unsupported language. Choose from: {', '.join(supported_languages)}[/red]")

    version_pattern = r"^\d+\.\d+\.\d+$"
    while True:
        version = typer.prompt("Version (e.g., 3.9.1)")
        if re.match(version_pattern, version):
            break
        console.print("[red]Invalid version format. Use semantic versioning (e.g., 3.9.1)[/red]")

    supported_audiences = ["newbie", "professional", "expert", "researcher", "contributor"]
    while True:
        audience = typer.prompt("Audience level", default="newbie")
        if audience.lower() in supported_audiences:
            break
        console.print(f"[red]Unsupported audience level. Choose from: {', '.join(supported_audiences)}[/red]")

    supported_details = ["basic", "medium", "high"]
    while True:
        detail = typer.prompt("Detail level", default="medium")
        if detail.lower() in supported_details:
            break
        console.print(f"[red]Unsupported detail level. Choose from: {', '.join(supported_details)}[/red]")

    supported_styles = ["historical", "logical", "general"]
    while True:
        style = typer.prompt("Explanation style", default="logical")
        if style.lower() in supported_styles:
            break
        console.print(f"[red]Unsupported style. Choose from: {', '.join(supported_styles)}[/red]")

    # content = typer.prompt("Documentation content")
    console.print("[bold]Opening editor for documentation[/bold]. [bold blue]Save and close to continue[/bold blue]")
    content = get_multiline_input_from_editor()

    taxonomy = load_taxonomy()
    metadata_path = select_metadata_path(taxonomy)

    metadata = {
        "language": language.lower(),
        "version": version,
        "audience": audience,
        "detail": detail,
        "style": style,
        "metadata_path": metadata_path,
        "timestamp": datetime.timestamp(datetime.now()),
    }

    doc_hash = hash_doc(metadata)
    file_path = DOCS_DIR / f"{language}_{version}_{doc_hash[:7]}.cbl"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        for key, value in metadata.items():
            f.write(f"### {key}: {value}\n")
        f.write("\n@audience({})\n".format(audience))
        f.write(content.strip() + "\n")
        f.write("---end---\n")

    console.print(f"[green]✔ Documentation saved as:[/green] {file_path}")
    return file_path


@app.command()
def push():
    console.rule("[bold magenta]Push Changes to GitHub[/bold magenta]")

    branch_name = f"docs/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    repo = Repo(".")
    git = repo.git

    # Ensure docs directory exists
    if not DOCS_DIR.exists():
        console.print("[red]No documentation found to push.[/red]")
        raise typer.Exit()

    # Git operations
    try:
        git.checkout("-b", branch_name)
        repo.git.add(DOCS_DIR.as_posix())
        repo.index.commit(f"📚 Add documentation [{branch_name}]")
        git.push("--set-upstream", "origin", branch_name)
        console.print(f"[green]✔ Pushed to origin as branch:[/green] {branch_name}")

        # Optional: Create PR using GitHub CLI
        subprocess.run(["gh", "pr", "create", "--fill", "--base", "main", "--head", branch_name])

    except Exception as e:
        console.print(f"[red]❌ Git error:[/red] {e}")
        raise typer.Exit()


@app.command()
def read(file: Path):
    """Read and display the content of a documentation file."""
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit()
    content = file.read_text()
    console.rule(f"[bold green]Content of {file.name}[/bold green]")
    console.print(content)


@app.command()
def read_filtered(language: str = typer.Option(None), max_version: str = typer.Option(None),
                  title: str = typer.Option(None)):
    """Search and select documentation by filters, then view one, with option to edit."""
    if not DOCS_DIR.exists():
        console.print("[red]No documentation directory found.[/red]")
        raise typer.Exit()

    files = list(DOCS_DIR.glob("*.cbl"))
    if not files:
        console.print("[yellow]No documentation files found.[/yellow]")
        raise typer.Exit()

    matches = []
    for file in files:
        metadata, sections = parse_cbl_file(file)
        if language and metadata.get("language") != language.lower():
            continue
        if max_version and parse_version(metadata.get("version")) >= parse_version(max_version):
            continue
        if title and not matches_title(metadata.get("metadata_path", ""), title):
            continue
        matches.append((file, metadata, sections))

    if not matches:
        console.print("[yellow]No documentation matched your search.[/yellow]")
        raise typer.Exit()

    console.print("[bold]Matched documentation titles:[/bold]")
    for i, (_, meta, _) in enumerate(matches, start=1):
        console.print(f"{i}. {meta.get('metadata_path', 'Untitled')}")

    while True:
        choice = typer.prompt(f"Enter the number of the document to view (1-{len(matches)})")
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            break
        console.print(f"[red]Please enter a valid number between 1 and {len(matches)}[/red]")

    selected_file, selected_meta, selected_sections = matches[int(choice) - 1]

    console.rule(f"[bold green]{selected_meta.get('metadata_path', selected_file.name)}[/bold green]")
    console.print(f"[blue]Language:[/blue] {selected_meta.get('language')}")
    console.print(f"[blue]Version:[/blue] {selected_meta.get('version')}")
    console.print(f"[blue]Audience:[/blue] {selected_meta.get('audience')}")
    console.print(f"[blue]Detail:[/blue] {selected_meta.get('detail')}")
    console.print(f"[blue]Style:[/blue] {selected_meta.get('style')}")
    console.print("[blue]Content:[/blue]")
    console.print(
        selected_sections.get(selected_meta["audience"], "[italic red]No content found for this audience[/italic red]"))

    edit_choice = typer.prompt("Do you want to edit this document? (y/N)").lower()
    if edit_choice == "y":
        editor = os.environ.get("EDITOR", "vim")
        subprocess.call([editor, str(selected_file)])
        console.print(f"[green]✔ Edited file saved:[/green] {selected_file}")


# Function to parse .cbl files with metadata and audience-based sections
def parse_cbl_file(path):
    with open(path, "r") as f:
        lines = f.read().splitlines()

    metadata = {}
    sections = {}
    current_section = None
    in_section = False

    for line in lines:
        if line.startswith("### "):
            key, value = line[4:].split(":", 1)
            metadata[key.strip()] = value.strip()
        elif line.startswith("@audience(") and line.endswith(")"):
            current_section = line[len("@audience("):-1]
            sections[current_section] = []
            in_section = True
        elif line.strip() == "---end---":
            in_section = False
            current_section = None
        elif in_section and current_section:
            sections[current_section].append(line)

    # Clean up sections
    for key in sections:
        sections[key] = "\n".join(sections[key])

    return metadata, sections


if __name__ == "__main__":
    app()
