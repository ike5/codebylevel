import typer
from rich.console import Console
from rich.table import Table

err_console = Console(stderr=True)


def main():
    err_console.print("[red]Here is something written to the standard error[/red]")


if __name__ == "__main__":
    typer.run(main)