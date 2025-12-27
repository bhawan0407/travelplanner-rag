"""LangGraph workflow for itinerary planning."""

from langgraph.graph import StateGraph, END
from typing import Dict, Any

from src.graph.state import PlannerState
from src.graph.nodes import (
    IntentAnalyzerNode,
    attraction_retriever_node,
    food_retriever_node,
    tips_retriever_node,
    itinerary_retriever_node,
    ContextAggregatorNode,
)


def should_replan(state: PlannerState) -> str:
    """Conditional edge: Check if replanning is needed.
    
    Args:
        state: Current planner state.
        
    Returns:
        Next node name: "generate" or "end".
    """
    if state.get("needs_replanning", False):
        # Check iteration count to avoid infinite loops
        if state.get("iteration_count", 0) < 3:
            return "generate"
    
    return "end"


def build_planning_graph() -> StateGraph:
    """Build the complete LangGraph workflow for itinerary planning.
    
    Returns:
        Compiled state graph.
    """
    # Create graph
    workflow = StateGraph(PlannerState)
    
    # Add nodes
    workflow.add_node("analyze_intent", IntentAnalyzerNode())
    workflow.add_node("retrieve_attractions", attraction_retriever_node)
    workflow.add_node("retrieve_food", food_retriever_node)
    workflow.add_node("retrieve_tips", tips_retriever_node)
    workflow.add_node("retrieve_itineraries", itinerary_retriever_node)
    workflow.add_node("aggregate_context", ContextAggregatorNode())
    
    # Note: We'll add generate, validate nodes in next iteration
    # For now, create a simplified flow
    
    # Set entry point
    workflow.set_entry_point("analyze_intent")
    
    # Connect nodes
    # After intent analysis, retrieve from all sources in parallel
    workflow.add_edge("analyze_intent", "retrieve_attractions")
    workflow.add_edge("analyze_intent", "retrieve_food")
    workflow.add_edge("analyze_intent", "retrieve_tips")
    workflow.add_edge("analyze_intent", "retrieve_itineraries")
    
    # After all retrievals, aggregate
    workflow.add_edge("retrieve_attractions", "aggregate_context")
    workflow.add_edge("retrieve_food", "aggregate_context")
    workflow.add_edge("retrieve_tips", "aggregate_context")
    workflow.add_edge("retrieve_itineraries", "aggregate_context")
    
    # For now, end after aggregation (we'll add generation next)
    workflow.add_edge("aggregate_context", END)
    
    # Compile and return
    return workflow.compile()


# Create global graph instance
planner_graph = build_planning_graph()