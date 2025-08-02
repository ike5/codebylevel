from packaging.version import parse as parse_version
import yaml
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

# Custom YAML representer for multiline strings
def str_presenter(dumper, data):
    if '\n' in data:  # multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

app = typer.Typer()
console = Console()
DOCS_DIR = Path("docs_by_level")


def get_multiline_input_from_editor() -> str:
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tf_path = tf.name
    editor = os.environ.get("EDITOR", "vi")
    subprocess.call([editor, tf_path])
    with open(tf_path, "r") as f:
        content = f.read()
    os.unlink(tf_path)
    return content


def format_multiline_yaml(content: str, indent: int = 2) -> str:
    lines = content.splitlines()
    if len(lines) == 1:
        return content  # single line, no need for block style
    indent_str = " " * indent
    indented_lines = [indent_str + line if line.strip() else "" for line in lines]
    return "|\n" + "\n".join(indented_lines)


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

    title = typer.prompt("Title for the documentation")

    # content = typer.prompt("Documentation content")
    console.print("[bold]Opening editor for documentation[/bold]. [bold blue]Save and close to continue[/bold blue]")
    content = get_multiline_input_from_editor()

    doc = {
        "language": language.lower(),
        "version": version,
        "audience": audience,
        "detail": detail,
        "style": style,
        "title": title,
        "content": format_multiline_yaml(content),
        "timestamp": datetime.timestamp(datetime.now()),
    }

    doc_hash = hash_doc(doc)
    file_path = DOCS_DIR / f"{language}_{version}_{doc_hash[:7]}.yaml"
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        yaml.dump(doc, f, sort_keys=False)

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

    files = list(DOCS_DIR.glob("*.yaml"))
    if not files:
        console.print("[yellow]No documentation files found.[/yellow]")
        raise typer.Exit()

    matches = []
    for file in files:
        with open(file, "r") as f:
            doc = yaml.safe_load(f)
            if language and doc.get("language") != language.lower():
                continue
            if max_version and parse_version(doc.get("version")) >= parse_version(max_version):
                continue
            if title and not matches_title(doc.get("title", ""), title):
                continue
            matches.append((file, doc))

    if not matches:
        console.print("[yellow]No documentation matched your search.[/yellow]")
        raise typer.Exit()

    console.print("[bold]Matched documentation titles:[/bold]")
    for i, (_, doc) in enumerate(matches, start=1):
        console.print(f"{i}. {doc.get('title', 'Untitled')}")

    while True:
        choice = typer.prompt(f"Enter the number of the document to view (1-{len(matches)})")
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            break
        console.print(f"[red]Please enter a valid number between 1 and {len(matches)}[/red]")

    selected_file, selected_doc = matches[int(choice) - 1]

    console.rule(f"[bold green]{selected_doc.get('title', selected_file.name)}[/bold green]")
    console.print(f"[blue]Language:[/blue] {selected_doc.get('language')}")
    console.print(f"[blue]Version:[/blue] {selected_doc.get('version')}")
    console.print(f"[blue]Audience:[/blue] {selected_doc.get('audience')}")
    console.print(f"[blue]Detail:[/blue] {selected_doc.get('detail')}")
    console.print(f"[blue]Style:[/blue] {selected_doc.get('style')}")
    console.print("[blue]Content:[/blue]")
    console.print(selected_doc.get("content"))

    edit_choice = typer.prompt("Do you want to edit this document? (y/N)").lower()
    if edit_choice == "y":
        editor = os.environ.get("EDITOR", "vim")
        subprocess.call([editor, str(selected_file)])
        console.print(f"[green]✔ Edited file saved:[/green] {selected_file}")


if __name__ == "__main__":
    app()
