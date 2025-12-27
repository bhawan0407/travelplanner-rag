"""Main CLI entry point for the travel planner."""

import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent))

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from datetime import datetime, timedelta

from src.models import UserPreferences, BudgetLevel, DietaryRestriction
from src.graph import planner_graph, PlannerState
from src.retrievers import MultiSourceRetriever

app = typer.Typer()
console = Console()


@app.command()
def plan(
    destination: str = typer.Option(..., "--destination", "-d", help="Destination city"),
    days: int = typer.Option(3, "--days", help="Number of days"),
    budget: str = typer.Option("moderate", "--budget", "-b", help="Budget level: budget, moderate, luxury"),
):
    """Generate a travel itinerary."""
    
    console.print("\n[bold cyan]🗺️  RAG Travel Planner[/bold cyan]\n")
    
    # Load knowledge bases
    console.print("Loading knowledge bases...")
    retriever = MultiSourceRetriever()
    retriever.load_all()
    console.print("✓ Knowledge bases loaded\n", style="green")
    
    # Build preferences
    budget_level = BudgetLevel(budget.lower())
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(days=days - 1)
    
    preferences = UserPreferences(
        destinations=[destination],
        start_date=start_date,
        end_date=end_date,
        budget_level=budget_level,
        dietary_restrictions=[],
        interests=["culture", "food"],
        avoid=[],
        pace="moderate",
        walking_preference=True,
    )
    
    console.print(f"[bold]Planning {days}-day trip to {destination}[/bold]")
    console.print(f"Budget: {budget_level.value}")
    console.print(f"Dates: {start_date.date()} to {end_date.date()}\n")
    
    # Run planning workflow
    initial_state: PlannerState = {
        "user_preferences": preferences,
        "errors": [],
        "warnings": [],
        "iteration_count": 0,
    }
    
    with console.status("[bold green]Planning your trip..."):
        result = planner_graph.invoke(initial_state)
    
    console.print("\n[bold green]✓ Planning complete![/bold green]\n")
    
    # Display aggregated context
    if "aggregated_context" in result:
        context = result["aggregated_context"]
        console.print("[bold]Retrieved Knowledge:[/bold]")
        console.print(context[:1000] + "..." if len(context) > 1000 else context)


@app.command()
def ingest():
    """Ingest data into vector stores."""
    from scripts.ingest_data import main as ingest_main
    ingest_main()


@app.command()
def interactive():
    """Interactive mode for building itineraries."""
    console.print("\n[bold cyan]🗺️  Interactive Travel Planner[/bold cyan]\n")
    
    # Get user input
    destination = Prompt.ask("Destination city")
    days = int(Prompt.ask("Number of days", default="3"))
    budget = Prompt.ask("Budget level", choices=["budget", "moderate", "luxury"], default="moderate")
    
    is_vegetarian = Confirm.ask("Any dietary restrictions (vegetarian)?", default=False)
    
    console.print(f"\n[bold]Planning {days}-day trip to {destination}![/bold]\n")
    
    # Build preferences
    budget_level = BudgetLevel(budget)
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(days=days - 1)
    
    dietary = [DietaryRestriction.VEGETARIAN] if is_vegetarian else []
    
    preferences = UserPreferences(
        destinations=[destination],
        start_date=start_date,
        end_date=end_date,
        budget_level=budget_level,
        dietary_restrictions=dietary,
        interests=["culture", "food"],
        avoid=[],
        pace="moderate",
        walking_preference=True,
    )
    
    # Load and run
    console.print("Loading knowledge bases...")
    retriever = MultiSourceRetriever()
    retriever.load_all()
    
    initial_state: PlannerState = {
        "user_preferences": preferences,
        "errors": [],
        "warnings": [],
        "iteration_count": 0,
    }
    
    with console.status("[bold green]Planning..."):
        result = planner_graph.invoke(initial_state)
    
    console.print("\n[bold green]✓ Complete![/bold green]\n")


if __name__ == "__main__":
    app()