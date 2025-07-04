"""
Planner Module - Converts natural language prompts into structured file generation plans.
"""

import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from agents.llm_utils import generate_code_with_llm
from agents.types import FileSpec, TechStack


class FileType(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    INTEGRATION = "integration"
    CONFIG = "config"
    DOCUMENTATION = "documentation"


@dataclass
class GenerationPlan:
    """Complete plan for repository generation."""
    project_name: str
    description: str
    tech_stack: Dict[str, TechStack]
    files: List[FileSpec]
    dependencies: List[str]
    integrations: List[str]
    estimated_complexity: int


class PromptAnalyzer:
    """Analyzes natural language prompts to extract requirements."""
    
    def __init__(self):
        self.tech_keywords = {
            'react': TechStack.REACT,
            'vue': TechStack.VUE,
            'angular': TechStack.ANGULAR,
            'flutter': TechStack.FLUTTER,
            'fastapi': TechStack.FASTAPI,
            'flask': TechStack.FLASK,
            'django': TechStack.DJANGO,
            'nodejs': TechStack.NODEJS,
            'node.js': TechStack.NODEJS,
            'postgresql': TechStack.POSTGRESQL,
            'postgres': TechStack.POSTGRESQL,
            'mongodb': TechStack.MONGODB,
            'mongo': TechStack.MONGODB,
            'mysql': TechStack.MYSQL,
            'sqlite': TechStack.SQLITE,
        }
        
        self.integration_keywords = {
            'stripe': 'payment',
            'paypal': 'payment',
            'firebase': 'backend_service',
            'supabase': 'backend_service',
            'auth0': 'authentication',
            'oauth': 'authentication',
            'google': 'authentication',
            'github': 'authentication',
            'sendgrid': 'email',
            'mailgun': 'email',
            'twilio': 'sms',
            'aws': 'cloud',
            'azure': 'cloud',
            'gcp': 'cloud',
            'docker': 'containerization',
            'kubernetes': 'orchestration',
        }
        
        self.feature_keywords = {
            'user': ['authentication', 'user_management'],
            'login': ['authentication'],
            'register': ['authentication', 'user_management'],
            'dashboard': ['frontend', 'analytics'],
            'admin': ['admin_panel', 'user_management'],
            'chat': ['real_time', 'messaging'],
            'message': ['messaging'],
            'notification': ['real_time', 'messaging'],
            'file': ['file_upload', 'storage'],
            'image': ['file_upload', 'storage'],
            'upload': ['file_upload', 'storage'],
            'payment': ['payment_processing'],
            'cart': ['e_commerce', 'shopping'],
            'shop': ['e_commerce', 'shopping'],
            'product': ['e_commerce', 'catalog'],
            'search': ['search_functionality'],
            'filter': ['search_functionality'],
            'api': ['backend', 'rest_api'],
            'database': ['database', 'data_storage'],
            'real-time': ['real_time', 'websockets'],
            'responsive': ['responsive_design'],
            'mobile': ['responsive_design', 'mobile_app'],
        }
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """Analyze a natural language prompt and extract requirements."""
        prompt_lower = prompt.lower()
        
        # Extract tech stack preferences
        tech_stack = {}
        for keyword, tech in self.tech_keywords.items():
            if keyword in prompt_lower:
                if tech.value in ['react', 'vue', 'angular', 'flutter']:
                    tech_stack['frontend'] = tech
                elif tech.value in ['fastapi', 'flask', 'django', 'nodejs']:
                    tech_stack['backend'] = tech
                elif tech.value in ['postgresql', 'mongodb', 'mysql', 'sqlite']:
                    tech_stack['database'] = tech
        
        # Set defaults if not specified
        if 'frontend' not in tech_stack:
            tech_stack['frontend'] = TechStack.REACT
        if 'backend' not in tech_stack:
            tech_stack['backend'] = TechStack.FASTAPI
        if 'database' not in tech_stack:
            tech_stack['database'] = TechStack.POSTGRESQL
        
        # Extract integrations
        integrations = []
        for keyword, integration_type in self.integration_keywords.items():
            if keyword in prompt_lower:
                integrations.append(integration_type)
        
        # Extract features
        features = set()
        for keyword, feature_list in self.feature_keywords.items():
            if keyword in prompt_lower:
                features.update(feature_list)
        
        # Determine project type
        project_type = self._determine_project_type(prompt_lower, features)
        
        # Extract project name
        project_name = self._extract_project_name(prompt)
        
        return {
            'project_name': project_name,
            'project_type': project_type,
            'tech_stack': tech_stack,
            'integrations': integrations,
            'features': list(features),
            'complexity': self._estimate_complexity(features, integrations)
        }
    
    def _determine_project_type(self, prompt: str, features: set) -> str:
        """Determine the type of project based on prompt and features."""
        if any(keyword in prompt for keyword in ['e-commerce', 'shop', 'store', 'cart']):
            return 'e_commerce'
        elif any(keyword in prompt for keyword in ['social', 'chat', 'message', 'social media']):
            return 'social_media'
        elif any(keyword in prompt for keyword in ['task', 'project', 'todo', 'management']):
            return 'project_management'
        elif any(keyword in prompt for keyword in ['blog', 'cms', 'content']):
            return 'content_management'
        elif any(keyword in prompt for keyword in ['finance', 'budget', 'expense']):
            return 'finance'
        elif any(keyword in prompt for keyword in ['education', 'learning', 'course']):
            return 'education'
        else:
            return 'web_application'
    
    def _extract_project_name(self, prompt: str) -> str:
        """Extract or generate a project name from the prompt."""
        # Look for patterns like "Create a [name] app" or "Build a [name] system"
        patterns = [
            r'create\s+a\s+([a-zA-Z\s]+)\s+(?:app|system|platform|website)',
            r'build\s+a\s+([a-zA-Z\s]+)\s+(?:app|system|platform|website)',
            r'develop\s+a\s+([a-zA-Z\s]+)\s+(?:app|system|platform|website)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                name = match.group(1).strip()
                # Convert to snake_case
                name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
                name = re.sub(r'\s+', '_', name)
                return name
        
        # If no specific name found, generate based on project type
        return "generated_project"
    
    def _estimate_complexity(self, features: List[str], integrations: List[str]) -> int:
        """Estimate project complexity on a scale of 1-10."""
        base_complexity = 3
        feature_complexity = len(features) * 0.5
        integration_complexity = len(integrations) * 1.5
        
        total_complexity = base_complexity + feature_complexity + integration_complexity
        return min(int(total_complexity), 10)


class ProjectPlanner:
    """Main planner class that creates generation plans."""
    
    def __init__(self):
        self.analyzer = PromptAnalyzer()
        self.file_templates = {
            'react': self._get_react_files,
            'vue': self._get_vue_files,
            'angular': self._get_angular_files,
            'fastapi': self._get_fastapi_files,
            'flask': self._get_flask_files,
            'django': self._get_django_files,
        }
    
    def create_plan(self, prompt: str) -> GenerationPlan:
        """Create a complete generation plan from a prompt."""
        analysis = self.analyzer.analyze_prompt(prompt)
        
        # Generate file specifications
        files = []
        files.extend(self._generate_frontend_files(analysis))
        files.extend(self._generate_backend_files(analysis))
        files.extend(self._generate_database_files(analysis))
        files.extend(self._generate_integration_files(analysis))
        files.extend(self._generate_config_files(analysis))
        files.extend(self._generate_documentation_files(analysis))
        
        # Create generation plan
        plan = GenerationPlan(
            project_name=analysis['project_name'],
            description=f"Generated {analysis['project_type']} application",
            tech_stack=analysis['tech_stack'],
            files=files,
            dependencies=self._get_dependencies(analysis),
            integrations=analysis['integrations'],
            estimated_complexity=analysis['complexity']
        )
        
        return plan
    
    def _generate_frontend_files(self, analysis: Dict) -> List[FileSpec]:
        """Generate frontend file specifications."""
        tech = analysis['tech_stack']['frontend']
        files = []
        
        if tech == TechStack.REACT:
            files.extend([
                FileSpec(
                    path="frontend/src/App.jsx",
                    type=FileType.FRONTEND,
                    agent="frontend_agent",
                    dependencies=[],
                    description="Main React application component",
                    priority=1,
                    tech_stack=tech
                ),
                FileSpec(
                    path="frontend/src/components/Header.jsx",
                    type=FileType.FRONTEND,
                    agent="frontend_agent",
                    dependencies=["App.jsx"],
                    description="Header component",
                    priority=2,
                    tech_stack=tech
                ),
                FileSpec(
                    path="frontend/src/pages/Home.jsx",
                    type=FileType.FRONTEND,
                    agent="frontend_agent",
                    dependencies=["App.jsx"],
                    description="Home page component",
                    priority=2,
                    tech_stack=tech
                ),
                FileSpec(
                    path="frontend/package.json",
                    type=FileType.CONFIG,
                    agent="frontend_agent",
                    dependencies=[],
                    description="Frontend package configuration",
                    priority=1,
                    tech_stack=tech
                ),
            ])
        
        # Add authentication components if needed
        if 'authentication' in analysis['features']:
            files.extend([
                FileSpec(
                    path="frontend/src/pages/Login.jsx",
                    type=FileType.FRONTEND,
                    agent="frontend_agent",
                    dependencies=["App.jsx"],
                    description="Login page component",
                    priority=2,
                    tech_stack=tech
                ),
                FileSpec(
                    path="frontend/src/pages/Register.jsx",
                    type=FileType.FRONTEND,
                    agent="frontend_agent",
                    dependencies=["App.jsx"],
                    description="Registration page component",
                    priority=2,
                    tech_stack=tech
                ),
            ])
        
        return files
    
    def _generate_backend_files(self, analysis: Dict) -> List[FileSpec]:
        """Generate backend file specifications."""
        tech = analysis['tech_stack']['backend']
        files = []
        
        if tech == TechStack.FASTAPI:
            files.extend([
                FileSpec(
                    path="backend/main.py",
                    type=FileType.BACKEND,
                    agent="backend_agent",
                    dependencies=[],
                    description="FastAPI main application",
                    priority=1,
                    tech_stack=tech
                ),
                FileSpec(
                    path="backend/routers/auth.py",
                    type=FileType.BACKEND,
                    agent="backend_agent",
                    dependencies=["main.py"],
                    description="Authentication routes",
                    priority=2,
                    tech_stack=tech
                ),
                FileSpec(
                    path="backend/models/user.py",
                    type=FileType.BACKEND,
                    agent="backend_agent",
                    dependencies=["main.py"],
                    description="User model",
                    priority=2,
                    tech_stack=tech
                ),
                FileSpec(
                    path="backend/requirements.txt",
                    type=FileType.CONFIG,
                    agent="backend_agent",
                    dependencies=[],
                    description="Backend dependencies",
                    priority=1,
                    tech_stack=tech
                ),
            ])
        
        return files
    
    def _generate_database_files(self, analysis: Dict) -> List[FileSpec]:
        """Generate database file specifications."""
        tech = analysis['tech_stack']['database']
        files = []
        
        files.extend([
            FileSpec(
                path="database/schema.sql",
                type=FileType.DATABASE,
                agent="database_agent",
                dependencies=[],
                description="Database schema definition",
                priority=1,
                tech_stack=tech
            ),
            FileSpec(
                path="database/migrations/001_initial.sql",
                type=FileType.DATABASE,
                agent="database_agent",
                dependencies=["schema.sql"],
                description="Initial database migration",
                priority=2,
                tech_stack=tech
            ),
        ])
        
        return files
    
    def _generate_integration_files(self, analysis: Dict) -> List[FileSpec]:
        """Generate integration file specifications."""
        files = []
        
        for integration in analysis['integrations']:
            if integration == 'payment':
                files.append(
                    FileSpec(
                        path="backend/integrations/payment.py",
                        type=FileType.INTEGRATION,
                        agent="integration_agent",
                        dependencies=["main.py"],
                        description="Payment integration (Stripe/PayPal)",
                        priority=3
                    )
                )
            elif integration == 'authentication':
                files.append(
                    FileSpec(
                        path="backend/integrations/oauth.py",
                        type=FileType.INTEGRATION,
                        agent="integration_agent",
                        dependencies=["main.py"],
                        description="OAuth integration",
                        priority=3
                    )
                )
        
        return files
    
    def _generate_config_files(self, analysis: Dict) -> List[FileSpec]:
        """Generate configuration file specifications."""
        files = [
            FileSpec(
                path="docker-compose.yml",
                type=FileType.CONFIG,
                agent="backend_agent",
                dependencies=[],
                description="Docker Compose configuration",
                priority=3
            ),
            FileSpec(
                path=".env.example",
                type=FileType.CONFIG,
                agent="backend_agent",
                dependencies=[],
                description="Environment variables example",
                priority=2
            ),
            FileSpec(
                path=".gitignore",
                type=FileType.CONFIG,
                agent="backend_agent",
                dependencies=[],
                description="Git ignore file",
                priority=3
            ),
        ]
        
        return files
    
    def _generate_documentation_files(self, analysis: Dict) -> List[FileSpec]:
        """Generate documentation file specifications."""
        files = [
            FileSpec(
                path="README.md",
                type=FileType.DOCUMENTATION,
                agent="refiner_agent",
                dependencies=[],
                description="Project documentation",
                priority=2
            ),
            FileSpec(
                path="docs/api.md",
                type=FileType.DOCUMENTATION,
                agent="refiner_agent",
                dependencies=["main.py"],
                description="API documentation",
                priority=3
            ),
        ]
        
        return files
    
    def _get_dependencies(self, analysis: Dict) -> List[str]:
        """Get project dependencies based on analysis."""
        dependencies = []
        
        # Frontend dependencies
        if analysis['tech_stack']['frontend'] == TechStack.REACT:
            dependencies.extend(['react', 'react-dom', 'react-router-dom'])
        
        # Backend dependencies
        if analysis['tech_stack']['backend'] == TechStack.FASTAPI:
            dependencies.extend(['fastapi', 'uvicorn', 'pydantic'])
        
        # Database dependencies
        if analysis['tech_stack']['database'] == TechStack.POSTGRESQL:
            dependencies.extend(['psycopg2-binary', 'sqlalchemy'])
        
        # Feature-specific dependencies
        if 'authentication' in analysis['features']:
            dependencies.extend(['python-jose', 'passlib', 'bcrypt'])
        
        if 'file_upload' in analysis['features']:
            dependencies.extend(['python-multipart', 'pillow'])
        
        return dependencies
    
    def _get_react_files(self):
        """Get React-specific file list."""
        return []
    
    def _get_vue_files(self):
        """Get Vue-specific file list."""
        return []
    
    def _get_angular_files(self):
        """Get Angular-specific file list."""
        return []
    
    def _get_fastapi_files(self):
        """Get FastAPI-specific file list."""
        return []
    
    def _get_flask_files(self):
        """Get Flask-specific file list."""
        return []
    
    def _get_django_files(self):
        """Get Django-specific file list."""
        return []


def create_generation_plan(prompt: str) -> GenerationPlan:
    """Create a generation plan from a natural language prompt."""
    planner = ProjectPlanner()
    return planner.create_plan(prompt)


class ZephyrPlanner:
    """Planner using Zephyr 1.3B LLM."""
    def plan(self, prompt: str) -> str:
        # This is a template for using Zephyr as the planner
        plan = generate_code_with_llm(
            f"Generate a file generation plan for the following prompt: {prompt}",
            agent_name='planner',
            max_new_tokens=512,
            temperature=0.2
        )
        return plan


if __name__ == "__main__":
    # Example usage
    prompt = "Create a task management app with user authentication, real-time updates, and file attachments"
    plan = create_generation_plan(prompt)
    
    print(f"Project: {plan.project_name}")
    print(f"Description: {plan.description}")
    print(f"Tech Stack: {plan.tech_stack}")
    print(f"Complexity: {plan.estimated_complexity}/10")
    print(f"Files to generate: {len(plan.files)}")
    
    for file_spec in plan.files:
        print(f"  - {file_spec.path} ({file_spec.agent})")