"""
Ticket Sales Agent - Main Entry Point
=====================================

This is the main orchestrator for the ticket sales agent that:
1. Fetches game information from Weaviate
2. Retrieves user history from Neo4j via MCP
3. Uses Strands agents to analyze and create context
4. Makes calls via VAPI with Realtime API
"""

import asyncio
import logging
from dotenv import load_dotenv

from src.agents.orchestrator import AgentOrchestrator
from src.databases.weaviate_client import WeaviateClient
from src.databases.neo4j_client import Neo4jClient
from src.vapi.caller import VAPIClient
from src.mcp.server import MCPServer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main execution function for the ticket sales agent."""
    logger.info("Starting Ticket Sales Agent...")
    
    try:
        # Initialize components
        weaviate_client = WeaviateClient()
        neo4j_client = Neo4jClient()
        vapi_client = VAPIClient()
        
        # Start MCP server
        mcp_server = MCPServer()
        await mcp_server.start()
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(
            weaviate_client=weaviate_client,
            neo4j_client=neo4j_client,
            vapi_client=vapi_client
        )
        
        # Start the sales agent process
        await orchestrator.run()
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        logger.info("Shutting down Ticket Sales Agent...")


if __name__ == "__main__":
    asyncio.run(main())
