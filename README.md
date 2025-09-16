# Ticket Sales Agent

An AI-powered ticket sales agent that uses multi-agent architecture to make personalized sales calls to customers.

## Architecture

The system consists of several integrated components:

### 🤖 Multi-Agent System (Strands-based)
- **Data Analyst Agent**: Analyzes user profiles, game history, and preferences
- **Orchestrator Agent**: Coordinates the entire sales process workflow

### 🗄️ Database Layer
- **Weaviate**: Vector database storing game information for semantic search
- **Neo4j**: Graph database storing user profiles, game history, and relationships
- **MCP Server**: Model Context Protocol server providing secure AI model access to Neo4j

### 📞 Communication Layer  
- **VAPI Integration**: Makes voice calls using OpenAI's Realtime API
- **Context-Aware Conversations**: Personalized conversations based on user data

## Features

- **Personalized Sales Calls**: Tailored conversations based on user history and preferences
- **Intelligent Game Matching**: Semantic search to find games matching user interests  
- **Multi-Agent Analysis**: Sophisticated user profiling and conversation strategy
- **Secure Data Access**: MCP protocol for safe AI-to-database communication
- **Real-time Voice Calls**: Natural conversations using OpenAI's Realtime API
- **Comprehensive Tracking**: Full interaction history and analytics

## Quick Start

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.template .env
```

Configure your environment variables:
```bash
# Required API Keys
VAPI_API_KEY=your_vapi_api_key
OPENAI_API_KEY=your_openai_api_key

# Database Connections  
WEAVIATE_URL=http://localhost:8080
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=your_neo4j_password
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

**Start Weaviate:**
```bash
docker run -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:latest
```

**Start Neo4j:**
```bash
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:latest
```

### 4. Run the System

```bash
python main.py
```

## Project Structure

```
src/
├── agents/                 # Multi-agent system
│   ├── base_agent.py      # Base agent class
│   ├── data_analyst_agent.py  # User/game analysis
│   └── orchestrator.py    # Main workflow coordination
├── databases/             # Database integrations
│   ├── weaviate_client.py # Game data (vector search)
│   └── neo4j_client.py    # User data (graph queries)
├── mcp/                   # Model Context Protocol
│   └── server.py          # MCP server for secure AI access
├── vapi/                  # Voice call integration
│   └── caller.py          # VAPI client and call management
└── utils/                 # Utilities
    └── config.py          # Configuration management

config/                    # Configuration files
tests/                     # Test files
scripts/                   # Utility scripts
```

## Usage Examples

### Single Sales Call

```python
from src.agents.orchestrator import AgentOrchestrator
from src.databases.weaviate_client import WeaviateClient
from src.databases.neo4j_client import Neo4jClient
from src.vapi.caller import VAPIClient

# Initialize components
weaviate = WeaviateClient()
neo4j = Neo4jClient()
vapi = VAPIClient()

# Create orchestrator
orchestrator = AgentOrchestrator(weaviate, neo4j, vapi)

# Make a sales call
result = await orchestrator.process_sales_call(
    user_id="user123",
    phone_number="+1234567890"
)

print(f"Call result: {result}")
```

### Batch Processing

```python
# Process multiple calls
user_list = [
    {"user_id": "user123", "phone_number": "+1234567890"},
    {"user_id": "user456", "phone_number": "+0987654321"}
]

results = await orchestrator.batch_process_calls(user_list)
print(f"Processed {results['summary']['successful']} successful calls")
```

## Key Components

### 🔍 Data Analysis
The Data Analyst Agent performs comprehensive user analysis:
- User segmentation (VIP Fan, Regular Attendee, etc.)
- Engagement level calculation
- Preference extraction from history
- Similar user identification
- Conversation strategy recommendations

### 🎮 Game Matching
Intelligent game recommendation using:
- Vector similarity search in Weaviate
- User preference matching
- Historical attendance patterns
- Team and sport preferences
- Venue and timing considerations

### 📞 Voice Calls
VAPI integration provides:
- Natural conversation flow
- Real-time speech processing
- Personalized context delivery
- Call recording and transcription
- Outcome tracking

### 🔒 Secure Data Access
MCP Server ensures:
- Secure AI model access to sensitive user data
- Structured data queries and responses
- Audit trail of data access
- Privacy-compliant data handling

## Configuration

All configuration is managed through environment variables and the `ConfigManager` class:

- **Database connections**: Weaviate and Neo4j endpoints
- **API keys**: VAPI and OpenAI credentials
- **Call settings**: Voice selection, duration limits, recording
- **Agent settings**: Temperature, token limits, retry logic

## Development

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`
2. Implement the `process_task` method
3. Register the agent in the orchestrator
4. Add task types and coordination logic

### Extending Database Schemas

1. Update the respective client classes
2. Add new MCP tools if needed
3. Update analysis logic in agents
4. Test with sample data

## Dependencies

- **Core**: FastAPI, asyncio, pydantic
- **Databases**: weaviate-client, neo4j, pymongo
- **AI/ML**: openai, strands-agent
- **Communication**: httpx, websockets, vapi
- **Utils**: python-dotenv, loguru, pyyaml

## License

[Add your license here]
