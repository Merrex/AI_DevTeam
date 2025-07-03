"""
File Writer - Saves generated code to disk with proper structure.
"""

import os
import asyncio
import aiofiles
from typing import Dict, List, Optional
from pathlib import Path
import shutil
import zipfile
from datetime import datetime


class FileWriter:
    """Handles writing generated files to disk."""
    
    def __init__(self, output_dir: str = "./generated_repos"):
        self.output_dir = output_dir
        self.created_directories = set()
        self.written_files = []
    
    async def write_file(self, file_path: str, content: str) -> bool:
        """Write a single file to disk."""
        try:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory and directory not in self.created_directories:
                os.makedirs(directory, exist_ok=True)
                self.created_directories.add(directory)
            
            # Write file content
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            self.written_files.append(file_path)
            return True
            
        except Exception as e:
            print(f"Error writing file {file_path}: {str(e)}")
            return False
    
    async def write_files(self, files: Dict[str, str], base_path: str = None) -> List[str]:
        """Write multiple files to disk."""
        if base_path:
            # Ensure base path exists
            os.makedirs(base_path, exist_ok=True)
        
        written_files = []
        
        # Write files concurrently
        tasks = []
        for file_path, content in files.items():
            full_path = os.path.join(base_path, file_path) if base_path else file_path
            tasks.append(self.write_file(full_path, content))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successfully written files
        for i, (file_path, result) in enumerate(zip(files.keys(), results)):
            if result is True:
                full_path = os.path.join(base_path, file_path) if base_path else file_path
                written_files.append(full_path)
        
        return written_files
    
    def create_project_structure(self, project_name: str, structure: Dict) -> str:
        """Create project directory structure."""
        project_path = os.path.join(self.output_dir, project_name)
        
        # Remove existing project if it exists
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        # Create project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create subdirectories
        self._create_directories(project_path, structure)
        
        return project_path
    
    def _create_directories(self, base_path: str, structure: Dict):
        """Recursively create directory structure."""
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                self._create_directories(path, content)
            else:
                # Create parent directory if it doesn't exist
                parent = os.path.dirname(path)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
    
    def create_zip_archive(self, project_path: str, archive_name: str = None) -> str:
        """Create a zip archive of the generated project."""
        if not archive_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = os.path.basename(project_path)
            archive_name = f"{project_name}_{timestamp}.zip"
        
        archive_path = os.path.join(self.output_dir, archive_name)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    def get_project_info(self, project_path: str) -> Dict:
        """Get information about the generated project."""
        if not os.path.exists(project_path):
            return {}
        
        info = {
            'project_name': os.path.basename(project_path),
            'project_path': project_path,
            'created_at': datetime.fromtimestamp(os.path.getctime(project_path)).isoformat(),
            'size_mb': self._get_directory_size(project_path) / (1024 * 1024),
            'file_count': self._count_files(project_path),
            'structure': self._get_directory_structure(project_path)
        }
        
        return info
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
        return total_size
    
    def _count_files(self, path: str) -> int:
        """Count total number of files in directory."""
        count = 0
        for root, dirs, files in os.walk(path):
            count += len(files)
        return count
    
    def _get_directory_structure(self, path: str, max_depth: int = 3) -> Dict:
        """Get directory structure up to max_depth."""
        def _build_structure(current_path: str, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth:
                return {}
            
            structure = {}
            try:
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    if os.path.isdir(item_path):
                        structure[item] = _build_structure(item_path, current_depth + 1)
                    else:
                        structure[item] = "file"
            except PermissionError:
                pass
            
            return structure
        
        return _build_structure(path)
    
    def list_generated_projects(self) -> List[Dict]:
        """List all generated projects."""
        projects = []
        
        if not os.path.exists(self.output_dir):
            return projects
        
        for item in os.listdir(self.output_dir):
            item_path = os.path.join(self.output_dir, item)
            if os.path.isdir(item_path):
                project_info = self.get_project_info(item_path)
                if project_info:
                    projects.append(project_info)
        
        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return projects
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a generated project."""
        project_path = os.path.join(self.output_dir, project_name)
        
        if not os.path.exists(project_path):
            return False
        
        try:
            shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"Error deleting project {project_name}: {str(e)}")
            return False
    
    def cleanup_old_projects(self, keep_count: int = 10) -> int:
        """Clean up old projects, keeping only the most recent ones."""
        projects = self.list_generated_projects()
        
        if len(projects) <= keep_count:
            return 0
        
        # Delete oldest projects
        deleted_count = 0
        for project in projects[keep_count:]:
            if self.delete_project(project['project_name']):
                deleted_count += 1
        
        return deleted_count
    
    async def save_generation_log(self, project_path: str, log_data: Dict) -> bool:
        """Save generation log for debugging and analysis."""
        log_path = os.path.join(project_path, '.generation_log.json')
        
        try:
            import json
            log_content = json.dumps(log_data, indent=2, default=str)
            return await self.write_file(log_path, log_content)
        except Exception as e:
            print(f"Error saving generation log: {str(e)}")
            return False
    
    def get_file_templates(self) -> Dict[str, str]:
        """Get common file templates."""
        templates = {
            'dockerfile_python': """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            'dockerfile_node': """FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
""",
            'makefile': """# Makefile for project management

.PHONY: install dev build test clean

install:
	pip install -r requirements.txt
	cd frontend && npm install

dev:
	docker-compose up -d

build:
	docker-compose build

test:
	python -m pytest
	cd frontend && npm test

clean:
	docker-compose down -v
	docker system prune -f

deploy:
	docker-compose -f docker-compose.prod.yml up -d
""",
            'github_workflow': """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest
    
    - name: Run linting
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
"""
        }
        
        return templates
    
    async def add_docker_support(self, project_path: str, tech_stack: Dict) -> bool:
        """Add Docker support to the project."""
        templates = self.get_file_templates()
        
        # Add Dockerfile for backend
        backend_dockerfile = os.path.join(project_path, 'backend', 'Dockerfile')
        await self.write_file(backend_dockerfile, templates['dockerfile_python'])
        
        # Add Dockerfile for frontend
        frontend_dockerfile = os.path.join(project_path, 'frontend', 'Dockerfile')
        await self.write_file(frontend_dockerfile, templates['dockerfile_node'])
        
        # Add Makefile
        makefile = os.path.join(project_path, 'Makefile')
        await self.write_file(makefile, templates['makefile'])
        
        return True
    
    async def add_ci_cd_support(self, project_path: str) -> bool:
        """Add CI/CD support to the project."""
        templates = self.get_file_templates()
        
        # Add GitHub Actions workflow
        workflow_dir = os.path.join(project_path, '.github', 'workflows')
        os.makedirs(workflow_dir, exist_ok=True)
        
        workflow_file = os.path.join(workflow_dir, 'ci.yml')
        await self.write_file(workflow_file, templates['github_workflow'])
        
        return True