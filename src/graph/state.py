"""State definition for the LangGraph workflow."""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

from src.models import UserPreferences, DayPlan, Itinerary


class PlannerState(TypedDict, total=False):
    """State passed through the LangGraph workflow.
    
    This state is shared and modified by different nodes in the graph.
    """
    
    # Input
    user_preferences: UserPreferences
    
    # Intent Analysis
    parsed_intent: Dict[str, Any]
    retrieval_strategy: Dict[str, Any]
    
    # Retrieved Context
    attractions_context: List[Dict[str, Any]]
    food_context: List[Dict[str, Any]]
    transport_context: List[Dict[str, Any]]
    tips_context: List[Dict[str, Any]]
    itinerary_context: List[Dict[str, Any]]
    
    # Aggregated Context
    aggregated_context: str
    
    # Generation
    draft_itinerary: Optional[Itinerary]
    
    # Validation
    validation_results: Dict[str, Any]
    constraints_met: Dict[str, bool]
    needs_replanning: bool
    replan_reason: Optional[str]
    
    # Final Output
    final_itinerary: Optional[Itinerary]
    
    # Error Handling
    errors: List[str]
    warnings: List[str]
    
    # Metadata
    iteration_count: int
    processing_time: float