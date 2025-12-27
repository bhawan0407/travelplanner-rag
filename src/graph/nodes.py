"""LangGraph nodes for the itinerary planning workflow."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from src.graph.state import PlannerState
from src.models import (
    UserPreferences,
    BudgetLevel,
    DietaryRestriction,
)
from src.retrievers import (
    MultiSourceRetriever,
    KnowledgeSource,
)
from src.config import settings


class IntentAnalyzerNode:
    """Analyzes user preferences and determines retrieval strategy."""

    def __call__(self, state: PlannerState) -> Dict[str, Any]:
        """Parse user preferences and decide what to retrieve.
        
        Args:
            state: Current planner state.
            
        Returns:
            Updated state with parsed intent and retrieval strategy.
        """
        prefs = state["user_preferences"]
        
        # Parse intent
        parsed_intent = {
            "destinations": prefs.destinations,
            "duration_days": (prefs.end_date - prefs.start_date).days + 1,
            "budget_level": prefs.budget_level,
            "dietary_needs": prefs.dietary_restrictions,
            "interests": prefs.interests,
            "avoid_list": prefs.avoid,
            "pace": prefs.pace,
            "walkable": prefs.walking_preference,
            "group_type": prefs.group_type,
        }
        
        # Determine retrieval strategy
        retrieval_strategy = {
            "sources": self._determine_sources(prefs),
            "filters": self._build_filters(prefs),
            "priority": self._determine_priority(prefs),
        }
        
        return {
            "parsed_intent": parsed_intent,
            "retrieval_strategy": retrieval_strategy,
            "errors": state.get("errors", []),
            "warnings": state.get("warnings", []),
        }

    def _determine_sources(self, prefs: UserPreferences) -> List[KnowledgeSource]:
        """Determine which knowledge sources to query."""
        sources = [
            KnowledgeSource.ATTRACTIONS,
            KnowledgeSource.FOOD,
            KnowledgeSource.TIPS,
        ]
        
        # Add past itineraries for similar trips
        sources.append(KnowledgeSource.ITINERARIES)
        
        return sources

    def _build_filters(self, prefs: UserPreferences) -> Dict[KnowledgeSource, Dict[str, Any]]:
        """Build filters for each knowledge source."""
        filters = {}
        
        # Attraction filters
        attraction_filters = {}
        if prefs.budget_level == BudgetLevel.BUDGET:
            attraction_filters["max_price"] = 10.0
        elif prefs.budget_level == BudgetLevel.MODERATE:
            attraction_filters["max_price"] = 25.0
        
        if prefs.avoid:
            attraction_filters["excluded_tags"] = prefs.avoid
        
        if prefs.interests:
            attraction_filters["required_tags"] = prefs.interests
        
        filters[KnowledgeSource.ATTRACTIONS] = attraction_filters
        
        # Food filters
        food_filters = {
            "dietary_restrictions": prefs.dietary_restrictions,
            "budget_level": prefs.budget_level,
        }
        filters[KnowledgeSource.FOOD] = food_filters
        
        # Itinerary filters
        itinerary_filters = {
            "duration_days": (prefs.end_date - prefs.start_date).days + 1,
        }
        filters[KnowledgeSource.ITINERARIES] = itinerary_filters
        
        return filters

    def _determine_priority(self, prefs: UserPreferences) -> List[str]:
        """Determine priority order for different aspects."""
        priorities = []
        
        if prefs.budget_level == BudgetLevel.BUDGET:
            priorities.append("cost")
        
        if prefs.walking_preference:
            priorities.append("proximity")
        
        if "food" in prefs.interests:
            priorities.append("culinary")
        
        return priorities


class ParallelRetrieverNode:
    """Retrieves information from multiple sources in parallel."""

    def __init__(self, source: KnowledgeSource):
        """Initialize retriever for a specific source.
        
        Args:
            source: Knowledge source to retrieve from.
        """
        self.source = source
        self.retriever = MultiSourceRetriever()

    def __call__(self, state: PlannerState) -> Dict[str, Any]:
        """Retrieve relevant information from the knowledge source.
        
        Args:
            state: Current planner state.
            
        Returns:
            Updated state with retrieved context.
        """
        strategy = state["retrieval_strategy"]
        prefs = state["user_preferences"]
        
        # Build query based on destination and interests
        query = self._build_query(prefs, self.source)
        
        # Get filters for this source
        filters = strategy["filters"].get(self.source, {})
        
        # Retrieve
        retriever = self.retriever._get_retriever(self.source)
        results = retriever.retrieve(
            query=query,
            k=settings.max_retrieval_results,
            filters=filters,
        )
        
        # Update state with source-specific context
        context_key = f"{self.source.value}_context"
        return {
            context_key: results,
        }

    def _build_query(self, prefs: UserPreferences, source: KnowledgeSource) -> str:
        """Build search query for this source."""
        destination = ", ".join(prefs.destinations)
        
        if source == KnowledgeSource.ATTRACTIONS:
            interests = ", ".join(prefs.interests) if prefs.interests else "popular attractions"
            return f"{destination} {interests} places to visit"
        
        elif source == KnowledgeSource.FOOD:
            dietary = ", ".join([d.value for d in prefs.dietary_restrictions])
            budget = prefs.budget_level.value
            return f"{destination} {budget} {dietary} restaurants"
        
        elif source == KnowledgeSource.TIPS:
            return f"{destination} travel tips local advice best time to visit"
        
        elif source == KnowledgeSource.ITINERARIES:
            duration = (prefs.end_date - prefs.start_date).days + 1
            return f"{destination} {duration} day itinerary {prefs.budget_level.value}"
        
        return destination


class ContextAggregatorNode:
    """Aggregates context from all retrievers into a coherent structure."""

    def __call__(self, state: PlannerState) -> Dict[str, Any]:
        """Aggregate retrieved context.
        
        Args:
            state: Current planner state.
            
        Returns:
            Updated state with aggregated context.
        """
        # Gather all context
        attractions = state.get("attractions_context", [])
        food = state.get("food_context", [])
        tips = state.get("tips_context", [])
        itineraries = state.get("itinerary_context", [])
        
        # Build structured context for LLM
        aggregated = self._build_context_string(
            attractions=attractions,
            food=food,
            tips=tips,
            itineraries=itineraries,
            preferences=state["user_preferences"],
        )
        
        return {
            "aggregated_context": aggregated,
        }

    def _build_context_string(
        self,
        attractions: List[Dict],
        food: List[Dict],
        tips: List[Dict],
        itineraries: List[Dict],
        preferences: UserPreferences,
    ) -> str:
        """Build formatted context string for the LLM."""
        sections = []
        
        # Trip summary
        duration = (preferences.end_date - preferences.start_date).days + 1
        sections.append(f"## Trip Planning Context\n")
        sections.append(f"Destinations: {', '.join(preferences.destinations)}")
        sections.append(f"Duration: {duration} days")
        sections.append(f"Budget: {preferences.budget_level.value}")
        sections.append(f"Group: {preferences.group_type or 'N/A'}\n")
        
        # Attractions
        if attractions:
            sections.append("## Available Attractions")
            for i, item in enumerate(attractions[:10], 1):
                sections.append(f"{i}. {item['text']}")
                sections.append(f"   Score: {item['score']:.2f}")
                sections.append(f"   Metadata: {json.dumps(item['metadata'])}\n")
        
        # Food
        if food:
            sections.append("## Food Options")
            for i, item in enumerate(food[:10], 1):
                sections.append(f"{i}. {item['text']}")
                sections.append(f"   Score: {item['score']:.2f}\n")
        
        # Tips
        if tips:
            sections.append("## Local Tips & Advice")
            for i, item in enumerate(tips[:5], 1):
                sections.append(f"- {item['text']}\n")
        
        # Past itineraries
        if itineraries:
            sections.append("## Similar Past Itineraries")
            for i, item in enumerate(itineraries[:3], 1):
                sections.append(f"{i}. {item['text'][:200]}...\n")
        
        return "\n".join(sections)


# Create retriever nodes for each source
attraction_retriever_node = ParallelRetrieverNode(KnowledgeSource.ATTRACTIONS)
food_retriever_node = ParallelRetrieverNode(KnowledgeSource.FOOD)
tips_retriever_node = ParallelRetrieverNode(KnowledgeSource.TIPS)
itinerary_retriever_node = ParallelRetrieverNode(KnowledgeSource.ITINERARIES)