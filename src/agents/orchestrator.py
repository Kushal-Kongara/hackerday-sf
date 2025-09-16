"""
Agent Orchestrator
==================

Main orchestrator that coordinates all agents and manages the overall workflow
for the ticket sales process.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from src.agents.base_agent import AgentTask, AgentResult, AgentStatus
from src.agents.data_analyst_agent import DataAnalystAgent
from src.databases.weaviate_client import WeaviateClient
from src.databases.neo4j_client import Neo4jClient
from src.vapi.caller import VAPIClient
from src.mcp.server import MCPServer

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main orchestrator for the multi-agent ticket sales system."""
    
    def __init__(self, weaviate_client: WeaviateClient, neo4j_client: Neo4jClient, vapi_client: VAPIClient):
        """
        Initialize the orchestrator.
        
        Args:
            weaviate_client: Client for game data
            neo4j_client: Client for user data
            vapi_client: Client for making calls
        """
        self.weaviate_client = weaviate_client
        self.neo4j_client = neo4j_client
        self.vapi_client = vapi_client
        
        # Initialize agents
        self.data_analyst = DataAnalystAgent()
        
        # Task tracking
        self.active_tasks = {}
        self.completed_tasks = {}
        
        logger.info("Agent Orchestrator initialized")
    
    async def process_sales_call(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """
        Process a complete sales call workflow.
        
        Args:
            user_id: Target user identifier
            phone_number: User's phone number
            
        Returns:
            Results of the sales call process
        """
        logger.info(f"Starting sales call process for user {user_id}")
        
        try:
            # Step 1: Gather user data from Neo4j
            user_data = await self._gather_user_data(user_id)
            if not user_data:
                return {"error": f"Could not retrieve data for user {user_id}"}
            
            # Step 2: Get relevant games from Weaviate
            game_data = await self._gather_game_data(user_data)
            
            # Step 3: Analyze user profile
            user_analysis = await self._analyze_user_profile(user_data)
            if not user_analysis:
                return {"error": "Failed to analyze user profile"}
            
            # Step 4: Match games to user
            game_matches = await self._match_games_to_user(user_analysis, game_data)
            if not game_matches:
                return {"error": "Failed to match games to user"}
            
            # Step 5: Generate conversation insights
            conversation_insights = await self._generate_conversation_insights(user_analysis, game_matches)
            if not conversation_insights:
                return {"error": "Failed to generate conversation insights"}
            
            # Step 6: Create call context and make the call
            call_result = await self._make_sales_call(user_id, phone_number, {
                "user_data": user_data,
                "user_analysis": user_analysis,
                "game_matches": game_matches,
                "insights": conversation_insights
            })
            
            # Step 7: Record the interaction
            await self._record_interaction(user_id, call_result)
            
            logger.info(f"Completed sales call process for user {user_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "call_result": call_result,
                "summary": {
                    "user_segment": user_analysis.get("analysis", {}).get("user_segment"),
                    "games_recommended": len(game_matches.get("matched_games", [])),
                    "call_initiated": call_result.get("call_data", {}).get("id") is not None
                }
            }
            
        except Exception as e:
            error_msg = f"Error in sales call process for user {user_id}: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def _gather_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Gather comprehensive user data from Neo4j."""
        try:
            profile = await self.neo4j_client.get_user_profile(user_id)
            if not profile:
                logger.warning(f"No profile found for user {user_id}")
                return None
            
            history = await self.neo4j_client.get_user_game_history(user_id, limit=20)
            preferences = await self.neo4j_client.get_user_preferences(user_id)
            similar_users = await self.neo4j_client.get_similar_users(user_id, limit=5)
            
            return {
                "profile": profile,
                "history": history,
                "preferences": preferences,
                "similar_users": similar_users
            }
            
        except Exception as e:
            logger.error(f"Error gathering user data for {user_id}: {e}")
            return None
    
    async def _gather_game_data(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather relevant game data from Weaviate based on user preferences."""
        try:
            # Build search queries based on user preferences
            search_queries = []
            
            preferences = user_data.get("preferences", {})
            favorite_teams = preferences.get("favorite_teams", [])
            favorite_sports = preferences.get("favorite_sports", [])
            
            # Search for preferred teams and sports
            for team in favorite_teams[:3]:  # Limit to top 3 teams
                search_queries.append(f"games {team}")
            
            for sport in favorite_sports[:2]:  # Limit to top 2 sports
                search_queries.append(f"{sport} games tickets")
            
            # Also search for upcoming games
            search_queries.append("upcoming games schedule")
            
            # Execute searches
            all_games = []
            for query in search_queries:
                games = await self.weaviate_client.search_games(query, limit=5)
                all_games.extend(games)
            
            # Remove duplicates and return
            unique_games = {game["id"]: game for game in all_games}
            return list(unique_games.values())[:10]  # Top 10 unique games
            
        except Exception as e:
            logger.error(f"Error gathering game data: {e}")
            return []
    
    async def _analyze_user_profile(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze user profile using the data analyst agent."""
        try:
            task = AgentTask(
                id=f"analyze_profile_{asyncio.get_event_loop().time()}",
                type="analyze_user_profile",
                data={"user_data": user_data}
            )
            
            result = await self.data_analyst.execute_task(task)
            
            if result.status == AgentStatus.COMPLETED:
                return result.data
            else:
                logger.error(f"User analysis failed: {result.error}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing user profile: {e}")
            return None
    
    async def _match_games_to_user(self, user_analysis: Dict[str, Any], 
                                 game_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Match games to user using the data analyst agent."""
        try:
            task = AgentTask(
                id=f"match_games_{asyncio.get_event_loop().time()}",
                type="match_games_to_user",
                data={
                    "user_analysis": user_analysis,
                    "available_games": game_data
                }
            )
            
            result = await self.data_analyst.execute_task(task)
            
            if result.status == AgentStatus.COMPLETED:
                return result.data
            else:
                logger.error(f"Game matching failed: {result.error}")
                return None
                
        except Exception as e:
            logger.error(f"Error matching games to user: {e}")
            return None
    
    async def _generate_conversation_insights(self, user_analysis: Dict[str, Any], 
                                            game_matches: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate conversation insights using the data analyst agent."""
        try:
            task = AgentTask(
                id=f"conversation_insights_{asyncio.get_event_loop().time()}",
                type="generate_conversation_insights",
                data={
                    "user_analysis": user_analysis,
                    "matched_games": game_matches.get("matched_games", [])
                }
            )
            
            result = await self.data_analyst.execute_task(task)
            
            if result.status == AgentStatus.COMPLETED:
                return result.data
            else:
                logger.error(f"Conversation insights generation failed: {result.error}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating conversation insights: {e}")
            return None
    
    async def _make_sales_call(self, user_id: str, phone_number: str, 
                             call_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make the actual sales call using VAPI."""
        try:
            # Create context for the AI assistant
            context = await self.vapi_client.create_call_context(
                user_data=call_context["user_data"],
                game_data=call_context["game_matches"].get("matched_games", [])
            )
            
            # Create assistant configuration
            assistant_config = await self.vapi_client.create_assistant(context)
            
            # Make the call
            call_result = await self.vapi_client.make_call(
                phone_number=phone_number,
                assistant_config=assistant_config
            )
            
            return {
                "call_data": call_result,
                "context_used": len(context),
                "games_promoted": len(call_context["game_matches"].get("matched_games", [])),
                "user_segment": call_context["user_analysis"].get("analysis", {}).get("user_segment")
            }
            
        except Exception as e:
            logger.error(f"Error making sales call: {e}")
            return {"error": str(e)}
    
    async def _record_interaction(self, user_id: str, call_result: Dict[str, Any]):
        """Record the interaction in Neo4j."""
        try:
            interaction_details = {
                "call_id": call_result.get("call_data", {}).get("id"),
                "games_promoted": call_result.get("games_promoted", 0),
                "user_segment": call_result.get("user_segment"),
                "context_size": call_result.get("context_used", 0),
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.neo4j_client.record_interaction(
                user_id=user_id,
                interaction_type="sales_call",
                details=interaction_details
            )
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
    
    async def batch_process_calls(self, user_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process multiple sales calls in batch.
        
        Args:
            user_list: List of user dictionaries with 'user_id' and 'phone_number'
            
        Returns:
            List of call results
        """
        logger.info(f"Processing batch of {len(user_list)} sales calls")
        
        # Create tasks for all calls
        tasks = []
        for user in user_list:
            task = self.process_sales_call(user["user_id"], user["phone_number"])
            tasks.append(task)
        
        # Execute all calls concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_calls = []
        failed_calls = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_calls.append({
                    "user_id": user_list[i]["user_id"],
                    "error": str(result)
                })
            elif result.get("success"):
                successful_calls.append(result)
            else:
                failed_calls.append({
                    "user_id": user_list[i]["user_id"],
                    "error": result.get("error", "Unknown error")
                })
        
        logger.info(f"Batch processing complete: {len(successful_calls)} successful, {len(failed_calls)} failed")
        
        return {
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "summary": {
                "total": len(user_list),
                "successful": len(successful_calls),
                "failed": len(failed_calls)
            }
        }
    
    async def run(self):
        """Main run loop for the orchestrator."""
        logger.info("Starting Agent Orchestrator main loop...")
        
        # This would typically run continuously, processing calls from a queue
        # For now, it's a placeholder for the main execution logic
        
        try:
            while True:
                # Check for new call requests
                # Process queued calls
                # Monitor active calls
                # Handle completions and failures
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            logger.info("Shutting down orchestrator...")
        except Exception as e:
            logger.error(f"Error in orchestrator main loop: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "orchestrator_status": "running",
            "agents": {
                "data_analyst": self.data_analyst.get_status()
            },
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "database_connections": {
                "weaviate": self.weaviate_client is not None,
                "neo4j": self.neo4j_client is not None
            }
        }
