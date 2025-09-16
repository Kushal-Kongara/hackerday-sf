"""
Neo4j Client for User and Game History
======================================

Handles all interactions with Neo4j graph database for user information and game attendance history.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, basic_auth

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Client for interacting with Neo4j graph database."""
    
    def __init__(self):
        """Initialize Neo4j client."""
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Connect to Neo4j instance."""
        try:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD")
            
            self.driver = GraphDatabase.driver(
                uri,
                auth=basic_auth(username, password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            logger.info("Connected to Neo4j successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile information.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User profile dictionary or None if not found
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})
                    RETURN u.id as id, u.name as name, u.email as email,
                           u.phone as phone, u.preferences as preferences,
                           u.created_at as created_at
                    """,
                    user_id=user_id
                )
                
                record = result.single()
                if record:
                    return dict(record)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user profile {user_id}: {e}")
            return None
    
    async def get_user_game_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's game attendance history.
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of records to return
            
        Returns:
            List of game attendance records
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[a:ATTENDED]->(g:Game)
                    RETURN g.id as game_id, g.title as game_title, 
                           g.date as game_date, g.venue as venue,
                           a.ticket_type as ticket_type, a.satisfaction_rating as rating,
                           a.attended_date as attended_date
                    ORDER BY a.attended_date DESC
                    LIMIT $limit
                    """,
                    user_id=user_id,
                    limit=limit
                )
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Error retrieving game history for user {user_id}: {e}")
            return []
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's preferences and interests.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary of user preferences
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})
                    OPTIONAL MATCH (u)-[i:INTERESTED_IN]->(t:Team)
                    OPTIONAL MATCH (u)-[p:PREFERS]->(s:Sport)
                    RETURN u.preferences as general_preferences,
                           collect(DISTINCT t.name) as favorite_teams,
                           collect(DISTINCT s.name) as favorite_sports
                    """,
                    user_id=user_id
                )
                
                record = result.single()
                if record:
                    return dict(record)
                return {}
                
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {e}")
            return {}
    
    async def get_similar_users(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find users with similar preferences and attendance patterns.
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of similar users to return
            
        Returns:
            List of similar users with similarity scores
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (u1:User {id: $user_id})-[:ATTENDED]->(g:Game)<-[:ATTENDED]-(u2:User)
                    WHERE u1 <> u2
                    WITH u2, count(g) as common_games
                    MATCH (u2)-[:ATTENDED]->(g2:Game)
                    WITH u2, common_games, count(g2) as total_games
                    RETURN u2.id as user_id, u2.name as name,
                           common_games, total_games,
                           (common_games * 1.0 / total_games) as similarity_score
                    ORDER BY similarity_score DESC
                    LIMIT $limit
                    """,
                    user_id=user_id,
                    limit=limit
                )
                
                return [dict(record) for record in result]
                
        except Exception as e:
            logger.error(f"Error finding similar users for {user_id}: {e}")
            return []
    
    async def record_interaction(self, user_id: str, interaction_type: str, 
                               details: Dict[str, Any]) -> bool:
        """
        Record a user interaction (call, purchase, etc.).
        
        Args:
            user_id: Unique user identifier
            interaction_type: Type of interaction (call, purchase, etc.)
            details: Additional interaction details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (u:User {id: $user_id})
                    CREATE (i:Interaction {
                        type: $interaction_type,
                        timestamp: datetime(),
                        details: $details
                    })
                    CREATE (u)-[:HAD_INTERACTION]->(i)
                    """,
                    user_id=user_id,
                    interaction_type=interaction_type,
                    details=details
                )
                
                logger.info(f"Recorded {interaction_type} interaction for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error recording interaction for user {user_id}: {e}")
            return False
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
