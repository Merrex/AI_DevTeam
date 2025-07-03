# DeepSeek Agentic Repository Generator

A modular AI agent system that generates full software codebases (frontend, backend, database, integrations, etc.) from a single natural language prompt.

## Architecture

The system consists of specialized agents that work together to generate complete software repositories:

- **Planner**: Converts natural language prompts into structured file generation plans
- **Frontend Agent**: Generates UI code (React, HTML, Flutter, etc.)
- **Backend Agent**: Generates API routes and services (FastAPI, Flask, etc.)
- **Database Agent**: Generates database schema, models, and queries
- **Integration Agent**: Adds third-party integrations (Firebase, Stripe, OAuth, etc.)
- **Refiner Agent**: Ensures code consistency and quality across all generated files

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Running the API Server

```bash
python main_api_server.py
```

The FastAPI server will start on `http://localhost:8000`

### Running the Streamlit UI

```bash
streamlit run ui_streamlit.py
```

## API Usage

### Generate Repository

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a task management app with user authentication, real-time updates, and file attachments"}'
```

### API Endpoints

- `POST /generate` - Generate a complete repository from a prompt
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## Project Structure

```
deepseek-agentic-repo-gen/
├── agents/
│   ├── __init__.py
│   ├── frontend_agent.py
│   ├── backend_agent.py
│   ├── integration_agent.py
│   ├── database_agent.py
│   └── refiner_agent.py
├── planner.py
├── repo_generator.py
├── file_writer.py
├── main_api_server.py
├── ui_streamlit.py
├── requirements.txt
└── README.md
```

## Features

- **Multi-Agent Architecture**: Specialized agents for different aspects of software development
- **Intelligent Planning**: Automatic analysis and breakdown of complex requirements
- **Full-Stack Generation**: Frontend, backend, database, and integration code
- **Code Refinement**: Automatic code review and consistency improvements
- **REST API**: Easy integration with other tools and services
- **Web Interface**: User-friendly Streamlit UI for interactive use
- **Extensible**: Easy to add new agents and capabilities

## Example Prompts

- "Create a social media app with user profiles, posts, comments, and real-time chat"
- "Build an e-commerce platform with product catalog, shopping cart, payment integration, and admin dashboard"
- "Generate a project management tool with task tracking, team collaboration, and reporting features"

## Configuration

The system can be configured through environment variables:

- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `OUTPUT_DIR`: Directory for generated repositories (default: `./generated_repos`)
- `MAX_FILE_SIZE`: Maximum size for generated files (default: 10MB)

## License

MIT License - see LICENSE file for details