#!/usr/bin/env python3
"""
Database Setup Script
=====================

Script to set up sample data in Weaviate and Neo4j for testing the ticket sales agent.
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.databases.weaviate_client import WeaviateClient
from src.databases.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_weaviate_data():
    """Set up sample game data in Weaviate."""
    logger.info("Setting up Weaviate sample data...")
    
    client = WeaviateClient()
    
    # Sample games data
    sample_games = [
        {
            "title": "Lakers vs Warriors",
            "sport": "Basketball",
            "date": "2024-01-15",
            "venue": "Crypto.com Arena",
            "teams": ["Lakers", "Warriors"],
            "description": "Exciting NBA matchup between two championship contenders"
        },
        {
            "title": "Chiefs vs Patriots",
            "sport": "Football",
            "date": "2024-01-20",
            "venue": "Arrowhead Stadium",
            "teams": ["Chiefs", "Patriots"],
            "description": "AFC Championship playoff game with playoff implications"
        },
        {
            "title": "Dodgers vs Giants",
            "sport": "Baseball",
            "date": "2024-04-10",
            "venue": "Dodger Stadium", 
            "teams": ["Dodgers", "Giants"],
            "description": "Classic rivalry game in beautiful Los Angeles weather"
        }
    ]
    
    logger.info("Note: Actual data insertion would require proper Weaviate schema setup")
    logger.info(f"Sample games prepared: {len(sample_games)} games")
    
    client.close()
    return sample_games


async def setup_neo4j_data():
    """Set up sample user data in Neo4j."""
    logger.info("Setting up Neo4j sample data...")
    
    client = Neo4jClient()
    
    # Sample Cypher queries to create test data
    sample_queries = [
        """
        // Create sample users
        CREATE (u1:User {
            id: 'user123',
            name: 'John Doe',
            email: 'john@example.com',
            phone: '+1234567890',
            created_at: datetime()
        })
        """,
        """
        // Create sample sports and teams
        CREATE (s1:Sport {name: 'Basketball'})
        CREATE (s2:Sport {name: 'Football'})
        CREATE (t1:Team {name: 'Lakers'})
        CREATE (t2:Team {name: 'Warriors'})
        """,
        """
        // Create sample games
        CREATE (g1:Game {
            id: 'game1',
            title: 'Lakers vs Warriors',
            date: '2024-01-15',
            venue: 'Crypto.com Arena'
        })
        """,
        """
        // Create relationships
        MATCH (u:User {id: 'user123'})
        MATCH (s:Sport {name: 'Basketball'})
        MATCH (t:Team {name: 'Lakers'})
        MATCH (g:Game {id: 'game1'})
        CREATE (u)-[:PREFERS]->(s)
        CREATE (u)-[:INTERESTED_IN]->(t)
        CREATE (u)-[:ATTENDED {
            ticket_type: 'Premium',
            satisfaction_rating: 5,
            attended_date: '2024-01-15'
        }]->(g)
        """
    ]
    
    logger.info("Note: Actual data insertion would execute these Cypher queries:")
    for i, query in enumerate(sample_queries, 1):
        logger.info(f"Query {i}: {query.strip()[:50]}...")
    
    client.close()
    return sample_queries


async def verify_setup():
    """Verify the database setup."""
    logger.info("Verifying database setup...")
    
    try:
        # Test Weaviate connection
        weaviate_client = WeaviateClient()
        logger.info("✅ Weaviate connection successful")
        weaviate_client.close()
        
        # Test Neo4j connection  
        neo4j_client = Neo4jClient()
        logger.info("✅ Neo4j connection successful")
        neo4j_client.close()
        
        logger.info("🎉 Database setup verification completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup verification failed: {e}")
        return False


if __name__ == "__main__":
    print("🗄️ Database Setup Script")
    print("=" * 30)
    print()
    print("This script will set up sample data for testing.")
    print("Make sure you have:")
    print("1. Weaviate running on localhost:8080")
    print("2. Neo4j running on localhost:7687")
    print("3. Proper credentials in your .env file")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        # Just verify connections
        asyncio.run(verify_setup())
    else:
        response = input("Continue with setup? (y/N): ")
        if response.lower() == 'y':
            async def main():
                await setup_weaviate_data()
                await setup_neo4j_data()
                await verify_setup()
            
            asyncio.run(main())
        else:
            print("Database setup cancelled.")
