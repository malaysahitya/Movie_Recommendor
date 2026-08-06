import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from app.models.request import RecommendationRequest
from app.agent.orchestrator import run_agent_pipeline

console = Console()

GENRE_OPTIONS = [
    "Action", "Comedy", "Drama", "Sci-Fi", "Romance", "Thriller",
    "Horror", "Animation", "Mystery", "Fantasy", "Crime", "Adventure"
]

INDUSTRY_OPTIONS = ["Hollywood", "Bollywood", "Anime"]

async def main_cli():
    console.print(Panel.fit("[bold magenta]🎬 MOVIE RECOMMENDER AGENT (ADK) 🎬[/bold magenta]\n[dim]Powered by Google Agent Development Kit[/dim]", border_style="magenta"))

    # Genre selection
    console.print("\n[bold cyan]Select a Genre from the list:[/bold cyan]")
    for idx, g in enumerate(GENRE_OPTIONS, 1):
        console.print(f"  [yellow]{idx}.[/yellow] {g}")
    
    g_choice = IntPrompt.ask("Enter Genre number", default=1)
    selected_genre = GENRE_OPTIONS[max(0, min(len(GENRE_OPTIONS)-1, g_choice - 1))]

    # Industry selection
    console.print("\n[bold cyan]Select Industry / Category:[/bold cyan]")
    for idx, ind in enumerate(INDUSTRY_OPTIONS, 1):
        console.print(f"  [yellow]{idx}.[/yellow] {ind}")
    
    ind_choice = IntPrompt.ask("Enter Industry number", default=1)
    selected_industry = INDUSTRY_OPTIONS[max(0, min(len(INDUSTRY_OPTIONS)-1, ind_choice - 1))]

    # Year Range inputs
    console.print("\n[bold cyan]Select Release Year Range:[/bold cyan]")
    start_year = IntPrompt.ask("Start Year", default=2015)
    end_year = IntPrompt.ask("End Year", default=2024)

    req = RecommendationRequest(
        genre=selected_genre,
        industry=selected_industry,
        start_year=start_year,
        end_year=end_year,
        limit=10,
        user_session_id="cli_session"
    )

    console.print("\n[bold green]🤖 Running 4-Agent Pipeline (Planner -> Researcher -> Analysis -> Explainer)...[/bold green]\n")
    
    response = await run_agent_pipeline(req)

    # Render Table of Top 10 Movies
    table = Table(title=f"🏆 Top 10 {selected_genre} Movies in {selected_industry} ({start_year} - {end_year})", border_style="cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold white", width=30)
    table.add_column("Year", style="yellow", width=8)
    table.add_column("Rating", style="bold green", width=8)
    table.add_column("Quality Index", style="magenta", width=12)
    table.add_column("Agent Reasoning", style="cyan")

    for idx, m in enumerate(response.movies, 1):
        table.add_row(
            str(idx),
            m.title,
            str(m.release_year),
            f"⭐ {m.rating}/10",
            f"{m.composite_score}/100",
            m.agent_reasoning[:80] + "..."
        )

    console.print(table)
    console.print(f"\n[dim]Executed in {response.execution_time_ms} ms. Session ID: {response.session_id}[/dim]\n")

if __name__ == "__main__":
    asyncio.run(main_cli())
