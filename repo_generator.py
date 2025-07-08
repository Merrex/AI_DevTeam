"""
Repository Generator - Coordinates all agents to generate a complete codebase.
"""

import os
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import traceback

from planner import GenerationPlan, FileSpec, create_generation_plan, ZephyrPlanner
from agents import (
    FrontendAgent, BackendAgent, DatabaseAgent, 
    IntegrationAgent, RefinerAgent
)
from agents.backend_agent import MistralBackendAgent
from agents.refiner_agent import WizardCoderRefiner
from file_writer import FileWriter
from agents.frontend_agent import MistralFrontendAgent
from agents.database_agent import MistralDatabaseAgent
from agents.integration_agent import MistralIntegrationAgent


@dataclass
class GenerationResult:
    """Result of code generation process."""
    success: bool
    project_path: str
    generated_files: List[str]
    errors: List[str]
    warnings: List[str]
    execution_time: float


class RepositoryGenerator:
    """Main coordinator for generating complete repositories."""
    
    def __init__(self, output_dir: str = "./generated_repos"):
        self.output_dir = output_dir
        # Use new agent pipeline
        self.planner = ZephyrPlanner()
        self.agents = {
            'frontend_agent': MistralFrontendAgent(),      # Use Mistral for frontend
            'backend_agent': MistralBackendAgent(),        # Use Mistral for backend
            'database_agent': MistralDatabaseAgent(),      # Use Mistral for database
            'integration_agent': MistralIntegrationAgent(),# Use Mistral for integration
            'refiner_agent': WizardCoderRefiner()          # Use WizardCoder for refinement
        }
        self.file_writer = FileWriter()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_repository(self, prompt: str) -> GenerationResult:
        """Generate a complete repository from a natural language prompt."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Use ZephyrPlanner for planning
            print("📋 Creating generation plan with Zephyr...")
            plan_str = self.planner.plan(prompt)
            # Optionally, parse plan_str into GenerationPlan if needed
            # For now, fallback to original planner for structure
            plan = create_generation_plan(prompt)
            
            # Step 2: Generate files using agents
            print("🔨 Generating files...")
            generated_files = await self._generate_files(plan)
            
            # Step 3: Refine code for consistency using WizardCoder
            print("✨ Refining code with WizardCoder...")
            refined_files = self.agents['refiner_agent'].refine(generated_files, plan)
            
            # Step 4: Write files to disk
            print("💾 Writing files...")
            project_path = await self._write_files(refined_files, plan)
            
            # Step 5: Generate additional project files
            print("📁 Generating project files...")
            await self._generate_project_files(project_path, plan)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return GenerationResult(
                success=True,
                project_path=project_path,
                generated_files=list(refined_files.keys()),
                errors=[],
                warnings=[],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            
            return GenerationResult(
                success=False,
                project_path="",
                generated_files=[],
                errors=[error_msg],
                warnings=[],
                execution_time=execution_time
            )
    
    async def _generate_files(self, plan: GenerationPlan) -> Dict[str, str]:
        """Generate all files using appropriate agents."""
        generated_files = {}
        
        # Create project context
        project_context = {
            'project_name': plan.project_name,
            'tech_stack': plan.tech_stack,
            'features': self._extract_features_from_plan(plan),
            'integrations': plan.integrations,
            'dependencies': plan.dependencies
        }
        
        # Sort files by priority
        sorted_files = sorted(plan.files, key=lambda f: f.priority)
        
        # Generate files with appropriate agents
        for file_spec in sorted_files:
            try:
                print(f"  📄 Generating {file_spec.path}...")
                
                # Get the appropriate agent
                agent = self.agents.get(file_spec.agent)
                if not agent:
                    print(f"    ⚠️  Unknown agent: {file_spec.agent}")
                    continue
                
                # Generate file content
                if hasattr(agent, 'generate_file'):
                    content = agent.generate_file(file_spec, project_context)
                else:
                    content = self._generate_generic_file(file_spec, project_context)
                
                generated_files[file_spec.path] = content
                
            except Exception as e:
                print(f"    ❌ Failed to generate {file_spec.path}: {str(e)}")
                # Continue with other files
                continue
        
        return generated_files
    
    def _generate_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate a generic file when no specific agent is available."""
        return f"""
# {file_spec.description}
# Generated file: {file_spec.path}
# Agent: {file_spec.agent}

# TODO: Implement {file_spec.description}
""".strip()
    
    def _extract_features_from_plan(self, plan: GenerationPlan) -> List[str]:
        """Extract features from generation plan."""
        features = []
        
        # Analyze file specs to determine features
        for file_spec in plan.files:
            if 'auth' in file_spec.path.lower():
                features.append('authentication')
            if 'task' in file_spec.path.lower():
                features.append('task_management')
            if 'payment' in file_spec.path.lower():
                features.append('payment_processing')
            if 'upload' in file_spec.path.lower() or 'file' in file_spec.path.lower():
                features.append('file_upload')
        
        return list(set(features))
    
    def _refine_code(self, files: Dict[str, str], plan: GenerationPlan) -> Dict[str, str]:
        """Refine all generated code for consistency."""
        refiner = self.agents['refiner_agent']
        
        project_context = {
            'project_name': plan.project_name,
            'tech_stack': plan.tech_stack,
            'features': self._extract_features_from_plan(plan),
            'integrations': plan.integrations
        }
        
        return refiner.ensure_consistency(files, project_context)
    
    async def _write_files(self, files: Dict[str, str], plan: GenerationPlan) -> str:
        """Write all files to disk."""
        project_path = os.path.join(self.output_dir, plan.project_name)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Write all files
        for file_path, content in files.items():
            full_path = os.path.join(project_path, file_path)
            await self.file_writer.write_file(full_path, content)
        
        return project_path
    
    async def _generate_project_files(self, project_path: str, plan: GenerationPlan):
        """Generate additional project files like README, .gitignore, etc."""
        
        # Generate README.md
        readme_content = self._generate_readme(plan)
        await self.file_writer.write_file(
            os.path.join(project_path, "README.md"), 
            readme_content
        )
        
        # Generate .gitignore
        gitignore_content = self._generate_gitignore(plan)
        await self.file_writer.write_file(
            os.path.join(project_path, ".gitignore"), 
            gitignore_content
        )
        
        # Generate .env.example
        env_example_content = self._generate_env_example(plan)
        await self.file_writer.write_file(
            os.path.join(project_path, ".env.example"), 
            env_example_content
        )
        
        # Generate docker-compose.yml if needed
        if any(tech.value in ['fastapi', 'flask', 'django'] for tech in plan.tech_stack.values()):
            docker_compose_content = self._generate_docker_compose(plan)
            await self.file_writer.write_file(
                os.path.join(project_path, "docker-compose.yml"), 
                docker_compose_content
            )
    
    def _generate_readme(self, plan: GenerationPlan) -> str:
        """Generate README.md content."""
        tech_stack_str = ", ".join([tech.value.title() for tech in plan.tech_stack.values()])
        integrations_str = ", ".join(plan.integrations) if plan.integrations else "None"
        
        return f"""# {plan.project_name}

{plan.description}

## Tech Stack

{tech_stack_str}

## Features

- Modern, responsive web application
- User authentication and authorization
- RESTful API with comprehensive endpoints
- Database integration with proper schema
- Third-party integrations
- Clean, maintainable code structure

## Integrations

{integrations_str}

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL (or your chosen database)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd {plan.project_name}
```

2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
npm install
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up the database
```bash
# Create database and run migrations
```

6. Start the development servers

Backend:
```bash
cd backend
python main.py
```

Frontend:
```bash
cd frontend
npm start
```

## API Documentation

The API documentation is available at `http://localhost:8000/docs` when running the backend server.

## Project Structure

```
{plan.project_name}/
├── backend/           # Backend API code
├── frontend/          # Frontend React app
├── database/          # Database schema and migrations
├── docs/              # Documentation
├── docker-compose.yml # Docker configuration
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
""".strip()
    
    def _generate_gitignore(self, plan: GenerationPlan) -> str:
        """Generate .gitignore content."""
        return """# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# React
/build
/coverage
.nyc_output

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
""".strip()
    
    def _generate_env_example(self, plan: GenerationPlan) -> str:
        """Generate .env.example content."""
        env_vars = [
            "# Database Configuration",
            "DATABASE_URL=postgresql://user:password@localhost:5432/dbname",
            "",
            "# JWT Configuration",
            "SECRET_KEY=your-secret-key-here",
            "ALGORITHM=HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            "",
            "# API Configuration",
            "API_HOST=localhost",
            "API_PORT=8000",
            "DEBUG=True",
            ""
        ]
        
        # Add integration-specific environment variables
        if 'payment' in plan.integrations:
            env_vars.extend([
                "# Stripe Configuration",
                "STRIPE_SECRET_KEY=sk_test_...",
                "STRIPE_PUBLISHABLE_KEY=pk_test_...",
                "STRIPE_WEBHOOK_SECRET=whsec_...",
                ""
            ])
        
        if 'email' in plan.integrations:
            env_vars.extend([
                "# Email Configuration",
                "SMTP_SERVER=smtp.gmail.com",
                "SMTP_PORT=587",
                "SMTP_USERNAME=your-email@gmail.com",
                "SMTP_PASSWORD=your-app-password",
                "SENDGRID_API_KEY=SG...",
                ""
            ])
        
        if 'authentication' in plan.integrations:
            env_vars.extend([
                "# OAuth Configuration",
                "GOOGLE_CLIENT_ID=your-google-client-id",
                "GOOGLE_CLIENT_SECRET=your-google-client-secret",
                "GITHUB_CLIENT_ID=your-github-client-id",
                "GITHUB_CLIENT_SECRET=your-github-client-secret",
                "OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback",
                ""
            ])
        
        if 'cloud' in plan.integrations:
            env_vars.extend([
                "# AWS Configuration",
                "AWS_ACCESS_KEY_ID=your-aws-access-key",
                "AWS_SECRET_ACCESS_KEY=your-aws-secret-key",
                "AWS_REGION=us-east-1",
                "S3_BUCKET_NAME=your-bucket-name",
                ""
            ])
        
        return "\n".join(env_vars)
    
    def _generate_docker_compose(self, plan: GenerationPlan) -> str:
        """Generate docker-compose.yml content."""
        backend_tech = plan.tech_stack.get('backend')
        db_tech = plan.tech_stack.get('database')
        
        services = {
            'backend': self._get_backend_service_config(backend_tech),
            'frontend': self._get_frontend_service_config(),
        }
        
        if db_tech:
            services['database'] = self._get_database_service_config(db_tech)
        
        compose_content = f"""version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@database:5432/{plan.project_name}
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - database
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start

  database:
    image: postgres:13
    environment:
      - POSTGRES_DB={plan.project_name}
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
""".strip()
        
        return compose_content
    
    def _get_backend_service_config(self, backend_tech) -> Dict:
        """Get backend service configuration for docker-compose."""
        return {
            'build': './backend',
            'ports': ['8000:8000'],
            'environment': [
                'DATABASE_URL=postgresql://user:password@database:5432/dbname',
                'SECRET_KEY=your-secret-key-here'
            ],
            'depends_on': ['database'],
            'volumes': ['./backend:/app'],
            'command': 'uvicorn main:app --host 0.0.0.0 --port 8000 --reload'
        }
    
    def _get_frontend_service_config(self) -> Dict:
        """Get frontend service configuration for docker-compose."""
        return {
            'build': './frontend',
            'ports': ['3000:3000'],
            'environment': [
                'REACT_APP_API_URL=http://localhost:8000'
            ],
            'depends_on': ['backend'],
            'volumes': ['./frontend:/app', '/app/node_modules'],
            'command': 'npm start'
        }
    
    def _get_database_service_config(self, db_tech) -> Dict:
        """Get database service configuration for docker-compose."""
        if db_tech.value == 'postgresql':
            return {
                'image': 'postgres:13',
                'environment': [
                    'POSTGRES_DB=dbname',
                    'POSTGRES_USER=user',
                    'POSTGRES_PASSWORD=password'
                ],
                'ports': ['5432:5432'],
                'volumes': ['postgres_data:/var/lib/postgresql/data']
            }
        elif db_tech.value == 'mysql':
            return {
                'image': 'mysql:8',
                'environment': [
                    'MYSQL_DATABASE=dbname',
                    'MYSQL_USER=user',
                    'MYSQL_PASSWORD=password',
                    'MYSQL_ROOT_PASSWORD=rootpassword'
                ],
                'ports': ['3306:3306'],
                'volumes': ['mysql_data:/var/lib/mysql']
            }
        elif db_tech.value == 'mongodb':
            return {
                'image': 'mongo:4.4',
                'environment': [
                    'MONGO_INITDB_ROOT_USERNAME=user',
                    'MONGO_INITDB_ROOT_PASSWORD=password'
                ],
                'ports': ['27017:27017'],
                'volumes': ['mongo_data:/data/db']
            }
        else:
            return {}


# Global repository generator instance
repo_generator = RepositoryGenerator()