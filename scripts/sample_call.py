#!/usr/bin/env python3
"""
Sample Script for Making a Test Call
====================================

This script demonstrates how to use the ticket sales agent to make a single call.
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.orchestrator import AgentOrchestrator
from src.databases.weaviate_client import WeaviateClient
from src.databases.neo4j_client import Neo4jClient
from src.vapi.caller import VAPIClient
from src.mcp.server import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def make_sample_call():
    """Make a sample sales call."""
    
    # Configuration
    USER_ID = "sample_user_123"
    PHONE_NUMBER = "+1234567890"  # Replace with a real test number
    
    logger.info("Initializing ticket sales agent components...")
    
    try:
        # Initialize database clients
        weaviate_client = WeaviateClient()
        neo4j_client = Neo4jClient()
        vapi_client = VAPIClient()
        
        # Start MCP server
        mcp_server = MCPServer()
        await mcp_server.start()
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(
            weaviate_client=weaviate_client,
            neo4j_client=neo4j_client,
            vapi_client=vapi_client
        )
        
        logger.info(f"Making sales call to user {USER_ID} at {PHONE_NUMBER}")
        
        # Process the sales call
        result = await orchestrator.process_sales_call(
            user_id=USER_ID,
            phone_number=PHONE_NUMBER
        )
        
        # Display results
        if result.get("success"):
            logger.info("✅ Sales call completed successfully!")
            
            summary = result.get("summary", {})
            logger.info(f"User Segment: {summary.get('user_segment', 'Unknown')}")
            logger.info(f"Games Recommended: {summary.get('games_recommended', 0)}")
            logger.info(f"Call Initiated: {'Yes' if summary.get('call_initiated') else 'No'}")
            
            call_data = result.get("call_result", {}).get("call_data", {})
            if call_data.get("id"):
                logger.info(f"Call ID: {call_data['id']}")
        else:
            logger.error(f"❌ Sales call failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in sample call: {e}")
        return {"error": str(e)}
    
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        if 'weaviate_client' in locals():
            weaviate_client.close()
        if 'neo4j_client' in locals():
            neo4j_client.close()
        if 'mcp_server' in locals():
            await mcp_server.stop()


async def check_system_status():
    """Check the status of all system components."""
    
    logger.info("Checking system status...")
    
    try:
        # Initialize components
        weaviate_client = WeaviateClient()
        neo4j_client = Neo4jClient()
        vapi_client = VAPIClient()
        
        orchestrator = AgentOrchestrator(
            weaviate_client=weaviate_client,
            neo4j_client=neo4j_client,
            vapi_client=vapi_client
        )
        
        # Get system status
        status = orchestrator.get_system_status()
        
        logger.info("📊 System Status:")
        logger.info(f"  Orchestrator: {status['orchestrator_status']}")
        logger.info(f"  Active Tasks: {status['active_tasks']}")
        logger.info(f"  Completed Tasks: {status['completed_tasks']}")
        
        logger.info("  Database Connections:")
        db_status = status['database_connections']
        logger.info(f"    Weaviate: {'✅ Connected' if db_status['weaviate'] else '❌ Disconnected'}")
        logger.info(f"    Neo4j: {'✅ Connected' if db_status['neo4j'] else '❌ Disconnected'}")
        
        logger.info("  Agents:")
        for agent_name, agent_status in status['agents'].items():
            logger.info(f"    {agent_name}: {agent_status['status']} "
                       f"(Queue: {agent_status['queued_tasks']}, "
                       f"Cache: {agent_status['cached_results']})")
        
        return status
        
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Check system status
        asyncio.run(check_system_status())
    else:
        # Make sample call
        print("🎫 Ticket Sales Agent - Sample Call")
        print("=" * 40)
        print()
        print("This script will make a sample sales call.")
        print("Make sure you have:")
        print("1. Configured your .env file with API keys")
        print("2. Started Weaviate and Neo4j databases")
        print("3. Updated the phone number in the script")
        print()
        
        response = input("Continue? (y/N): ")
        if response.lower() == 'y':
            asyncio.run(make_sample_call())
        else:
            print("Sample call cancelled.")
