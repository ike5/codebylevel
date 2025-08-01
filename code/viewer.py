import frontmatter
import typer

def render_doc(file_path: str, user_license: str):
    try:
        post = frontmatter.load(file_path)
    except Exception as e:
        typer.secho(f"❌ Failed to read file: {e}", fg=typer.colors.RED)
        return

    meta = post.metadata
    body = post.content

    # Access control
    if meta.get("access") == "private":
        allowed = meta.get("license", "") in [user_license, "free"] or user_license in ["contributor", "paid"]
        if not allowed:
            typer.secho("🚫 This documentation is marked as private.", fg=typer.colors.RED)
            typer.secho("🔐 You need a contributor or paid license to view it.", fg=typer.colors.YELLOW)
            return

    # Render
    typer.secho(f"\n📘 {meta.get('title')} ({meta.get('language')} {meta.get('version')})", bold=True)
    typer.secho("-" * 60)
    print(body)