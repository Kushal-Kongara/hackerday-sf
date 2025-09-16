"""
Data Analyst Agent
==================

Analyzes user data from Neo4j and game data from Weaviate to create insights
for the sales conversation.
"""

import logging
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentTask, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class DataAnalystAgent(BaseAgent):
    """Agent responsible for analyzing user and game data."""
    
    def __init__(self):
        super().__init__("data_analyst", "Data Analyst Agent")
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process data analysis tasks."""
        
        if task.type == "analyze_user_profile":
            return await self._analyze_user_profile(task)
        elif task.type == "match_games_to_user":
            return await self._match_games_to_user(task)
        elif task.type == "generate_conversation_insights":
            return await self._generate_conversation_insights(task)
        else:
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=f"Unknown task type: {task.type}"
            )
    
    async def _analyze_user_profile(self, task: AgentTask) -> AgentResult:
        """
        Analyze user profile data to extract key insights.
        
        Args:
            task: Task containing user profile data
            
        Returns:
            Analysis results
        """
        try:
            user_data = task.data.get("user_data", {})
            profile = user_data.get("profile", {})
            history = user_data.get("history", [])
            preferences = user_data.get("preferences", {})
            
            analysis = {
                "user_segment": self._determine_user_segment(history, preferences),
                "engagement_level": self._calculate_engagement_level(history),
                "preferred_categories": self._extract_preferred_categories(history, preferences),
                "spending_pattern": self._analyze_spending_pattern(history),
                "last_activity": self._get_last_activity(history),
                "contact_preferences": self._determine_contact_preferences(profile),
                "risk_factors": self._identify_risk_factors(history, preferences)
            }
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data={"analysis": analysis}
            )
            
        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    async def _match_games_to_user(self, task: AgentTask) -> AgentResult:
        """
        Match available games to user preferences and history.
        
        Args:
            task: Task containing user analysis and available games
            
        Returns:
            Matched games with scores
        """
        try:
            user_analysis = task.data.get("user_analysis", {})
            available_games = task.data.get("available_games", [])
            
            matched_games = []
            
            for game in available_games:
                score = self._calculate_game_match_score(game, user_analysis)
                reasons = self._generate_match_reasons(game, user_analysis)
                
                matched_games.append({
                    "game": game,
                    "match_score": score,
                    "reasons": reasons,
                    "priority": "high" if score > 0.8 else "medium" if score > 0.6 else "low"
                })
            
            # Sort by match score
            matched_games.sort(key=lambda x: x["match_score"], reverse=True)
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data={"matched_games": matched_games[:5]}  # Top 5 matches
            )
            
        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    async def _generate_conversation_insights(self, task: AgentTask) -> AgentResult:
        """
        Generate insights for the sales conversation.
        
        Args:
            task: Task containing all user and game analysis
            
        Returns:
            Conversation insights and talking points
        """
        try:
            user_analysis = task.data.get("user_analysis", {})
            matched_games = task.data.get("matched_games", [])
            
            insights = {
                "opening_approach": self._suggest_opening_approach(user_analysis),
                "key_talking_points": self._generate_talking_points(user_analysis, matched_games),
                "potential_objections": self._predict_objections(user_analysis),
                "recommended_offers": self._suggest_offers(matched_games),
                "conversation_style": self._recommend_conversation_style(user_analysis),
                "best_contact_time": self._suggest_contact_time(user_analysis),
                "follow_up_strategy": self._plan_follow_up_strategy(user_analysis)
            }
            
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data={"insights": insights}
            )
            
        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    def _determine_user_segment(self, history: List[Dict], preferences: Dict) -> str:
        """Determine user segment based on history and preferences."""
        if len(history) >= 10:
            return "VIP_Fan"
        elif len(history) >= 5:
            return "Regular_Attendee"
        elif len(history) >= 2:
            return "Occasional_Fan"
        elif preferences.get("favorite_teams") or preferences.get("favorite_sports"):
            return "Interested_Prospect"
        else:
            return "New_Prospect"
    
    def _calculate_engagement_level(self, history: List[Dict]) -> str:
        """Calculate user engagement level."""
        if not history:
            return "Low"
        
        recent_games = [g for g in history if g.get("attended_date")][:5]
        avg_rating = sum(g.get("satisfaction_rating", 3) for g in recent_games) / len(recent_games)
        
        if avg_rating >= 4.5:
            return "High"
        elif avg_rating >= 3.5:
            return "Medium"
        else:
            return "Low"
    
    def _extract_preferred_categories(self, history: List[Dict], preferences: Dict) -> List[str]:
        """Extract preferred game categories."""
        categories = set()
        
        # From explicit preferences
        for team in preferences.get("favorite_teams", []):
            categories.add(f"Team: {team}")
        
        for sport in preferences.get("favorite_sports", []):
            categories.add(f"Sport: {sport}")
        
        # From history patterns
        # This would be more sophisticated in a real implementation
        
        return list(categories)
    
    def _analyze_spending_pattern(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze user spending patterns."""
        if not history:
            return {"pattern": "Unknown", "average_ticket_type": "Standard"}
        
        ticket_types = [g.get("ticket_type", "Standard") for g in history]
        premium_count = sum(1 for t in ticket_types if "Premium" in t or "VIP" in t)
        
        return {
            "pattern": "High-Value" if premium_count / len(ticket_types) > 0.3 else "Value-Conscious",
            "average_ticket_type": max(set(ticket_types), key=ticket_types.count),
            "premium_preference": premium_count / len(ticket_types)
        }
    
    def _get_last_activity(self, history: List[Dict]) -> Dict[str, Any]:
        """Get information about last activity."""
        if not history:
            return {"status": "No prior activity"}
        
        latest = max(history, key=lambda x: x.get("attended_date", ""))
        return {
            "game": latest.get("game_title", "Unknown"),
            "date": latest.get("attended_date", "Unknown"),
            "satisfaction": latest.get("satisfaction_rating", 3)
        }
    
    def _determine_contact_preferences(self, profile: Dict) -> Dict[str, str]:
        """Determine preferred contact methods and times."""
        return {
            "preferred_method": "phone",  # Could be derived from profile
            "best_time": "evening",       # Could be derived from history
            "tone": "friendly"            # Could be derived from past interactions
        }
    
    def _identify_risk_factors(self, history: List[Dict], preferences: Dict) -> List[str]:
        """Identify potential risk factors for the sale."""
        risks = []
        
        if not history:
            risks.append("No purchase history")
        
        if history:
            recent_ratings = [g.get("satisfaction_rating", 3) for g in history[:3]]
            if sum(recent_ratings) / len(recent_ratings) < 3:
                risks.append("Recent low satisfaction")
        
        return risks
    
    def _calculate_game_match_score(self, game: Dict, user_analysis: Dict) -> float:
        """Calculate how well a game matches the user."""
        # This would be more sophisticated in a real implementation
        # considering team preferences, sport preferences, venue, time, etc.
        base_score = 0.5
        
        # Add scoring logic based on user preferences
        # This is a simplified example
        
        return min(base_score + 0.3, 1.0)  # Cap at 1.0
    
    def _generate_match_reasons(self, game: Dict, user_analysis: Dict) -> List[str]:
        """Generate reasons why this game matches the user."""
        reasons = []
        
        # This would analyze game properties against user preferences
        # and generate human-readable reasons
        
        reasons.append("Matches your favorite sport")
        reasons.append("Similar to games you've enjoyed before")
        
        return reasons
    
    def _suggest_opening_approach(self, user_analysis: Dict) -> str:
        """Suggest how to open the conversation."""
        segment = user_analysis.get("user_segment", "New_Prospect")
        
        if segment == "VIP_Fan":
            return "Reference their loyalty and offer exclusive opportunities"
        elif segment == "Regular_Attendee":
            return "Mention their attendance history and suggest similar games"
        else:
            return "Focus on introducing the experience and building interest"
    
    def _generate_talking_points(self, user_analysis: Dict, matched_games: List[Dict]) -> List[str]:
        """Generate key talking points for the conversation."""
        points = []
        
        if matched_games:
            top_game = matched_games[0]["game"]
            points.append(f"Highlight the {top_game.get('properties', {}).get('title', 'upcoming game')}")
        
        points.append("Emphasize the unique atmosphere and experience")
        points.append("Mention any special promotions or deals")
        
        return points
    
    def _predict_objections(self, user_analysis: Dict) -> List[Dict[str, str]]:
        """Predict potential objections and responses."""
        return [
            {
                "objection": "Price concerns",
                "response": "Emphasize value and payment options"
            },
            {
                "objection": "Schedule conflicts",
                "response": "Offer alternative dates or flexible options"
            }
        ]
    
    def _suggest_offers(self, matched_games: List[Dict]) -> List[Dict[str, Any]]:
        """Suggest specific offers to make."""
        offers = []
        
        if matched_games:
            for game in matched_games[:2]:
                offers.append({
                    "game": game["game"],
                    "offer_type": "Standard discount",
                    "urgency": "Limited time"
                })
        
        return offers
    
    def _recommend_conversation_style(self, user_analysis: Dict) -> str:
        """Recommend conversation style based on user profile."""
        engagement = user_analysis.get("engagement_level", "Medium")
        
        if engagement == "High":
            return "Enthusiastic and knowledgeable"
        elif engagement == "Medium":
            return "Friendly and informative"
        else:
            return "Educational and patient"
    
    def _suggest_contact_time(self, user_analysis: Dict) -> str:
        """Suggest best time to contact."""
        return "Early evening (6-8 PM)"  # Could be more sophisticated
    
    def _plan_follow_up_strategy(self, user_analysis: Dict) -> Dict[str, str]:
        """Plan follow-up strategy."""
        return {
            "timing": "24-48 hours if interested, 1 week if undecided",
            "method": "Phone call followed by email with details",
            "content": "Personalized game recommendations based on conversation"
        }
