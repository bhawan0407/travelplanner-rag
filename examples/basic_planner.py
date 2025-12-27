"""Basic example of using the travel planner."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models import UserPreferences, BudgetLevel, DietaryRestriction
from src.graph import planner_graph, PlannerState
from src.retrievers import MultiSourceRetriever


def example_basic_plan():
    """Example: Generate a basic 3-day Paris itinerary."""
    
    print("=" * 60)
    print("Basic Travel Planner Example")
    print("=" * 60)
    
    # Load vector stores
    print("\nLoading knowledge bases...")
    retriever = MultiSourceRetriever()
    retriever.load_all()
    print("✓ Knowledge bases loaded")
    
    # Define user preferences
    preferences = UserPreferences(
        destinations=["Paris"],
        start_date=datetime(2024, 6, 15),
        end_date=datetime(2024, 6, 17),  # 3 days
        budget_level=BudgetLevel.BUDGET,
        dietary_restrictions=[DietaryRestriction.VEGETARIAN],
        interests=["art", "history", "food"],
        avoid=["crowds"],
        pace="moderate",
        walking_preference=True,
        group_type="couple",
    )
    
    print("\nUser Preferences:")
    print(f"  Destinations: {preferences.destinations}")
    print(f"  Duration: {(preferences.end_date - preferences.start_date).days + 1} days")
    print(f"  Budget: {preferences.budget_level.value}")
    print(f"  Dietary: {[d.value for d in preferences.dietary_restrictions]}")
    print(f"  Interests: {preferences.interests}")
    
    # Initialize state
    initial_state: PlannerState = {
        "user_preferences": preferences,
        "errors": [],
        "warnings": [],
        "iteration_count": 0,
    }
    
    # Run the graph
    print("\n" + "=" * 60)
    print("Running Planning Workflow...")
    print("=" * 60)
    
    try:
        result = planner_graph.invoke(initial_state)
        
        print("\n✓ Planning workflow completed!")
        
        # Display results
        print("\n" + "=" * 60)
        print("Results")
        print("=" * 60)
        
        # Show parsed intent
        if "parsed_intent" in result:
            print("\n📋 Parsed Intent:")
            for key, value in result["parsed_intent"].items():
                print(f"  {key}: {value}")
        
        # Show retrieval strategy
        if "retrieval_strategy" in result:
            print("\n🎯 Retrieval Strategy:")
            strategy = result["retrieval_strategy"]
            print(f"  Sources: {[s.value for s in strategy.get('sources', [])]}")
            print(f"  Priority: {strategy.get('priority', [])}")
        
        # Show retrieved context counts
        print("\n📚 Retrieved Context:")
        for key in ["attractions_context", "food_context", "tips_context", "itinerary_context"]:
            if key in result:
                count = len(result[key])
                print(f"  {key}: {count} items")
        
        # Show aggregated context (truncated)
        if "aggregated_context" in result:
            context = result["aggregated_context"]
            print(f"\n📄 Aggregated Context ({len(context)} characters):")
            print(context[:500] + "..." if len(context) > 500 else context)
        
        print("\n" + "=" * 60)
        print("Example complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during planning: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    example_basic_plan()