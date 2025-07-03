"""
Main API Server - FastAPI server for the repository generation system.
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
from datetime import datetime
import logging

from repo_generator import RepositoryGenerator, GenerationResult
from file_writer import FileWriter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DeepSeek Agentic Repository Generator",
    description="Generate complete software codebases from natural language prompts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
repo_generator = RepositoryGenerator()
file_writer = FileWriter()

# In-memory storage for generation status (use Redis/database in production)
generation_status = {}


# Pydantic models
class GenerationRequest(BaseModel):
    prompt: str
    project_name: Optional[str] = None
    output_format: Optional[str] = "files"  # "files" or "zip"
    options: Optional[Dict[str, Any]] = None


class GenerationStatusResponse(BaseModel):
    task_id: str
    status: str  # "pending", "in_progress", "completed", "failed"
    progress: float
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProjectInfo(BaseModel):
    project_name: str
    project_path: str
    created_at: str
    size_mb: float
    file_count: int
    structure: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float


# Global variables for tracking
start_time = datetime.now()
generation_counter = 0


@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    logger.info("Starting DeepSeek Agentic Repository Generator API")
    
    # Create output directory
    os.makedirs(repo_generator.output_dir, exist_ok=True)
    
    logger.info(f"Output directory: {repo_generator.output_dir}")
    logger.info("API server started successfully")


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "DeepSeek Agentic Repository Generator",
        "version": "1.0.0",
        "description": "Generate complete software codebases from natural language prompts",
        "docs_url": "/docs",
        "status": "healthy"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now() - start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=uptime
    )


@app.post("/generate", response_class=JSONResponse)
async def generate_repository(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate a repository from a natural language prompt."""
    global generation_counter
    generation_counter += 1
    
    # Create unique task ID
    task_id = f"gen_{generation_counter}_{int(datetime.now().timestamp())}"
    
    # Initialize generation status
    generation_status[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "message": "Generation request received",
        "started_at": datetime.now(),
        "completed_at": None,
        "result": None,
        "error": None,
        "prompt": request.prompt
    }
    
    # Start generation in background
    background_tasks.add_task(
        run_generation,
        task_id,
        request.prompt,
        request.project_name,
        request.output_format,
        request.options or {}
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Generation started",
        "check_status_url": f"/status/{task_id}"
    }


@app.get("/status/{task_id}", response_model=GenerationStatusResponse)
async def get_generation_status(task_id: str):
    """Get the status of a generation task."""
    if task_id not in generation_status:
        raise HTTPException(
            status_code=404,
            detail="Generation task not found"
        )
    
    status_data = generation_status[task_id]
    
    return GenerationStatusResponse(
        task_id=status_data["task_id"],
        status=status_data["status"],
        progress=status_data["progress"],
        message=status_data["message"],
        started_at=status_data["started_at"],
        completed_at=status_data["completed_at"],
        result=status_data["result"],
        error=status_data["error"]
    )


@app.get("/projects", response_class=JSONResponse)
async def list_projects():
    """List all generated projects."""
    try:
        projects = file_writer.list_generated_projects()
        return {
            "projects": projects,
            "total": len(projects)
        }
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list projects"
        )


@app.get("/projects/{project_name}", response_model=ProjectInfo)
async def get_project_info(project_name: str):
    """Get information about a specific project."""
    try:
        project_path = os.path.join(repo_generator.output_dir, project_name)
        project_info = file_writer.get_project_info(project_path)
        
        if not project_info:
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
        
        return ProjectInfo(**project_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get project information"
        )


@app.get("/projects/{project_name}/download")
async def download_project(project_name: str):
    """Download a project as a zip file."""
    try:
        project_path = os.path.join(repo_generator.output_dir, project_name)
        
        if not os.path.exists(project_path):
            raise HTTPException(
                status_code=404,
                detail="Project not found"
            )
        
        # Create zip archive
        zip_path = file_writer.create_zip_archive(project_path)
        
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"{project_name}.zip"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading project: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download project"
        )


@app.delete("/projects/{project_name}")
async def delete_project(project_name: str):
    """Delete a generated project."""
    try:
        success = file_writer.delete_project(project_name)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Project not found or could not be deleted"
            )
        
        return {"message": f"Project {project_name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete project"
        )


@app.post("/cleanup")
async def cleanup_old_projects(keep_count: int = 10):
    """Clean up old projects, keeping only the most recent ones."""
    try:
        deleted_count = file_writer.cleanup_old_projects(keep_count)
        
        return {
            "message": f"Cleaned up {deleted_count} old projects",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"Error cleaning up projects: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clean up projects"
        )


@app.get("/tasks", response_class=JSONResponse)
async def list_generation_tasks():
    """List all generation tasks and their status."""
    return {
        "tasks": list(generation_status.values()),
        "total": len(generation_status)
    }


async def run_generation(
    task_id: str,
    prompt: str,
    project_name: Optional[str],
    output_format: str,
    options: Dict[str, Any]
):
    """Run the generation process in the background."""
    try:
        # Update status
        generation_status[task_id]["status"] = "in_progress"
        generation_status[task_id]["progress"] = 0.1
        generation_status[task_id]["message"] = "Analyzing prompt..."
        
        # Generate repository
        result = await repo_generator.generate_repository(prompt)
        
        # Update progress
        generation_status[task_id]["progress"] = 0.8
        generation_status[task_id]["message"] = "Finalizing generation..."
        
        if result.success:
            # Handle output format
            final_result = {
                "project_path": result.project_path,
                "generated_files": result.generated_files,
                "execution_time": result.execution_time
            }
            
            if output_format == "zip":
                # Create zip archive
                zip_path = file_writer.create_zip_archive(result.project_path)
                final_result["download_url"] = f"/projects/{os.path.basename(result.project_path)}/download"
            
            # Update status - success
            generation_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "Generation completed successfully",
                "completed_at": datetime.now(),
                "result": final_result
            })
            
            logger.info(f"Generation {task_id} completed successfully")
        else:
            # Update status - failed
            generation_status[task_id].update({
                "status": "failed",
                "progress": 0.0,
                "message": "Generation failed",
                "completed_at": datetime.now(),
                "error": "; ".join(result.errors)
            })
            
            logger.error(f"Generation {task_id} failed: {result.errors}")
    
    except Exception as e:
        # Update status - error
        generation_status[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": "Generation failed with error",
            "completed_at": datetime.now(),
            "error": str(e)
        })
        
        logger.error(f"Generation {task_id} failed with exception: {str(e)}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Run the server
    uvicorn.run(
        "main_api_server:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )