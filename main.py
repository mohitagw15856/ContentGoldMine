#!/usr/bin/env python3
"""ContentGoldMine — CLI & launcher entry point."""
import typer
import uvicorn
import subprocess
import sys
from pathlib import Path

app = typer.Typer(help="⛏️ ContentGoldMine — Turn any content into multi-platform gold.")


@app.command()
def webui(
    port: int = typer.Option(8501, help="Streamlit port"),
):
    """Launch the Streamlit web UI."""
    typer.echo("⛏️  Starting ContentGoldMine Web UI...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app/webui.py", f"--server.port={port}"],
        check=True,
    )


@app.command()
def api(
    host: str = typer.Option("0.0.0.0", help="API host"),
    port: int = typer.Option(8000, help="API port"),
    reload: bool = typer.Option(False, help="Auto-reload on changes"),
):
    """Launch the FastAPI backend."""
    typer.echo(f"⛏️  Starting ContentGoldMine API on http://{host}:{port}")
    uvicorn.run("app.api:app", host=host, port=port, reload=reload)


@app.command()
def repurpose(
    input_type: str = typer.Argument(help="Input type: url | youtube | text"),
    value: str = typer.Argument(help="URL or text to repurpose"),
    provider: str = typer.Option("openai", "--provider", "-p", help="LLM provider"),
    api_key: str = typer.Option(..., "--key", "-k", envvar="OPENAI_API_KEY", help="API key"),
    language: str = typer.Option("English", "--lang", "-l"),
    platforms: str = typer.Option("all", "--platforms", help="Comma-separated platforms or 'all'"),
):
    """Repurpose content from the command line."""
    from goldmine.engine import GoldMineEngine
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    selected = None if platforms == "all" else [p.strip() for p in platforms.split(",")]

    engine = GoldMineEngine(llm_provider=provider, api_key=api_key, language=language)

    with console.status("[gold1]⛏️  Mining your content...[/gold1]"):
        results = engine.repurpose(input_type, value, selected)

    for key, output in results["outputs"].items():
        if "error" in output:
            console.print(f"[red]✗ {key}: {output['error']}[/red]")
        else:
            console.print(Panel(
                output["raw"][:800] + ("..." if len(output["raw"]) > 800 else ""),
                title=f"[gold1]{output['emoji']} {output['platform']}[/gold1]",
                border_style="dark_goldenrod",
            ))


if __name__ == "__main__":
    app()
