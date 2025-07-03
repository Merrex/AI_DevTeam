import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.backend_agent import BackendAgent
from planner import FileSpec, TechStack

if __name__ == "__main__":
    agent = BackendAgent()
    # Build a minimal FileSpec for testing
    file_spec = FileSpec(
        path="backend/routers/auth.py",
        type=None,
        agent="backend_agent",
        dependencies=[],
        description="Create a FastAPI endpoint for user registration using JWT auth.",
        priority=1,
        tech_stack=TechStack.FASTAPI
    )
    project_context = {
        'project_name': 'llm-test',
        'tech_stack': {'backend': 'fastapi'},
        'features': ['authentication'],
        'integrations': [],
        'dependencies': []
    }
    output = agent.generate_file(file_spec, project_context, use_llm=True)

    print("\n=== Generated Code ===\n")
    print(output) 