"""
Weaviate Client for Game Information
===================================

Handles all interactions with Weaviate vector database for game information retrieval.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import weaviate
from weaviate.classes.config import Configure

logger = logging.getLogger(__name__)


class WeaviateClient:
    """Client for interacting with Weaviate vector database."""
    
    def __init__(self):
        """Initialize Weaviate client."""
        self.client = None
        self.collection_name = "Games"
        self._connect()
    
    def _connect(self):
        """Connect to Weaviate instance."""
        try:
            weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            api_key = os.getenv("WEAVIATE_API_KEY")
            
            if api_key:
                self.client = weaviate.connect_to_custom(
                    http_host=weaviate_url.replace("http://", "").replace("https://", ""),
                    http_port=8080,
                    http_secure=False,
                    auth_credentials=weaviate.auth.AuthApiKey(api_key)
                )
            else:
                self.client = weaviate.connect_to_local()
            
            logger.info("Connected to Weaviate successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
    
    async def search_games(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for games using vector similarity.
        
        Args:
            query: Search query about games
            limit: Maximum number of results
            
        Returns:
            List of game information dictionaries
        """
        try:
            games = self.client.collections.get(self.collection_name)
            
            response = games.query.near_text(
                query=query,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(
                    score=True,
                    distance=True
                )
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "id": obj.uuid,
                    "properties": obj.properties,
                    "score": obj.metadata.score,
                    "distance": obj.metadata.distance
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching games: {e}")
            return []
    
    async def get_game_by_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific game information by ID.
        
        Args:
            game_id: Unique game identifier
            
        Returns:
            Game information dictionary or None if not found
        """
        try:
            games = self.client.collections.get(self.collection_name)
            game = games.query.fetch_object_by_id(game_id)
            
            if game:
                return {
                    "id": game.uuid,
                    "properties": game.properties
                }
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving game {game_id}: {e}")
            return None
    
    async def get_upcoming_games(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming games within specified days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming games
        """
        # This would typically use date filtering
        # Implementation depends on your game data schema
        try:
            games = self.client.collections.get(self.collection_name)
            
            response = games.query.near_text(
                query="upcoming games schedule",
                limit=10
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "id": obj.uuid,
                    "properties": obj.properties
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving upcoming games: {e}")
            return []
    
    def close(self):
        """Close the Weaviate connection."""
        if self.client:
            self.client.close()
            logger.info("Weaviate connection closed")
