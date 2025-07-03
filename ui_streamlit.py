"""
Streamlit UI for the DeepSeek Agentic Repository Generator.
"""

import streamlit as st
import requests
import time
import json
import os
from datetime import datetime
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="DeepSeek Agentic Repo Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def main():
    """Main Streamlit application."""
    st.title("🚀 DeepSeek Agentic Repository Generator")
    st.markdown("Generate complete software codebases from natural language prompts")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Home", "📋 Generate Repository", "📊 Project Manager", "📈 Analytics"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📋 Generate Repository":
        show_generation_page()
    elif page == "📊 Project Manager":
        show_project_manager()
    elif page == "📈 Analytics":
        show_analytics_page()


def show_home_page():
    """Show the home page with system information."""
    st.header("Welcome to DeepSeek Agentic Repository Generator")
    
    # System health check
    with st.spinner("Checking system health..."):
        health_status = check_api_health()
    
    if health_status:
        st.success("✅ System is healthy and ready to generate code!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("API Status", "Healthy")
        
        with col2:
            st.metric("Version", health_status.get("version", "Unknown"))
        
        with col3:
            uptime_hours = health_status.get("uptime", 0) / 3600
            st.metric("Uptime", f"{uptime_hours:.1f}h")
    else:
        st.error("❌ System is not available. Please check the API server.")
    
    st.markdown("---")
    
    # Feature overview
    st.subheader("🎯 Features")
    
    features = [
        "🎨 **Frontend Generation**: React, Vue, Angular, Flutter",
        "🔧 **Backend Generation**: FastAPI, Flask, Django, Node.js",
        "🗄️ **Database Integration**: PostgreSQL, MySQL, MongoDB, SQLite",
        "🔗 **Third-party Integrations**: Stripe, OAuth, AWS, SendGrid",
        "📝 **Code Refinement**: Automatic code quality and consistency checks",
        "🚀 **Production Ready**: Docker, CI/CD, comprehensive documentation"
    ]
    
    for feature in features:
        st.markdown(feature)
    
    st.markdown("---")
    
    # Example prompts
    st.subheader("💡 Example Prompts")
    
    examples = [
        "Create a task management app with user authentication, real-time updates, and file attachments",
        "Build an e-commerce platform with product catalog, shopping cart, payment integration, and admin dashboard",
        "Generate a social media app with user profiles, posts, comments, and real-time chat",
        "Create a project management tool with task tracking, team collaboration, and reporting features",
        "Build a blog platform with CMS, user authentication, commenting system, and SEO optimization"
    ]
    
    selected_example = st.selectbox("Choose an example prompt:", [""] + examples)
    
    if selected_example:
        if st.button("🚀 Generate with this prompt"):
            st.session_state.selected_prompt = selected_example
            st.experimental_rerun()


def show_generation_page():
    """Show the repository generation page."""
    st.header("📋 Generate Repository")
    
    # Generation form
    with st.form("generation_form"):
        st.subheader("Project Details")
        
        # Get prompt from session state if available
        default_prompt = st.session_state.get("selected_prompt", "")
        
        prompt = st.text_area(
            "Describe your project:",
            value=default_prompt,
            height=150,
            placeholder="E.g., Create a task management app with user authentication, real-time updates, and file attachments"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name (optional):",
                placeholder="my-awesome-project"
            )
        
        with col2:
            output_format = st.selectbox(
                "Output Format:",
                ["files", "zip"],
                help="Choose whether to generate files or create a downloadable zip"
            )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                include_docker = st.checkbox("Include Docker support", value=True)
                include_ci_cd = st.checkbox("Include CI/CD pipeline", value=True)
            
            with col2:
                include_tests = st.checkbox("Include test files", value=True)
                include_docs = st.checkbox("Include documentation", value=True)
        
        submitted = st.form_submit_button("🚀 Generate Repository")
    
    # Process generation request
    if submitted:
        if not prompt.strip():
            st.error("Please provide a project description.")
            return
        
        # Clear previous prompt from session state
        if "selected_prompt" in st.session_state:
            del st.session_state.selected_prompt
        
        # Prepare request data
        request_data = {
            "prompt": prompt,
            "project_name": project_name or None,
            "output_format": output_format,
            "options": {
                "include_docker": include_docker,
                "include_ci_cd": include_ci_cd,
                "include_tests": include_tests,
                "include_docs": include_docs
            }
        }
        
        # Start generation
        with st.spinner("Starting generation..."):
            response = start_generation(request_data)
        
        if response:
            st.success("✅ Generation started successfully!")
            task_id = response["task_id"]
            
            # Monitor generation progress
            monitor_generation(task_id)
        else:
            st.error("❌ Failed to start generation. Please try again.")


def show_project_manager():
    """Show the project management page."""
    st.header("📊 Project Manager")
    
    # Refresh button
    if st.button("🔄 Refresh Projects"):
        st.experimental_rerun()
    
    # Load projects
    with st.spinner("Loading projects..."):
        projects = load_projects()
    
    if not projects:
        st.info("No projects found. Generate your first repository!")
        return
    
    # Display projects
    st.subheader(f"Projects ({len(projects)})")
    
    for project in projects:
        with st.expander(f"📁 {project['project_name']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Files", project['file_count'])
            
            with col2:
                st.metric("Size", f"{project['size_mb']:.2f} MB")
            
            with col3:
                created_date = datetime.fromisoformat(project['created_at']).strftime("%Y-%m-%d %H:%M")
                st.text(f"Created: {created_date}")
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"📥 Download", key=f"download_{project['project_name']}"):
                    download_project(project['project_name'])
            
            with col2:
                if st.button(f"ℹ️ Info", key=f"info_{project['project_name']}"):
                    show_project_info(project)
            
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{project['project_name']}"):
                    delete_project(project['project_name'])


def show_analytics_page():
    """Show the analytics page."""
    st.header("📈 Analytics")
    
    # Load generation tasks
    with st.spinner("Loading analytics data..."):
        tasks = load_generation_tasks()
    
    if not tasks:
        st.info("No generation tasks found.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(tasks)
    
    # Statistics
    st.subheader("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Generations", len(df))
    
    with col2:
        successful = len(df[df['status'] == 'completed'])
        st.metric("Successful", successful)
    
    with col3:
        failed = len(df[df['status'] == 'failed'])
        st.metric("Failed", failed)
    
    with col4:
        if successful > 0:
            success_rate = (successful / len(df)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "0%")
    
    # Status distribution
    st.subheader("📊 Status Distribution")
    status_counts = df['status'].value_counts()
    st.bar_chart(status_counts)
    
    # Recent tasks
    st.subheader("📋 Recent Tasks")
    recent_tasks = df.tail(10)
    
    for _, task in recent_tasks.iterrows():
        with st.expander(f"Task {task['task_id']} - {task['status']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text(f"Status: {task['status']}")
                st.text(f"Progress: {task['progress']:.1%}")
            
            with col2:
                started = datetime.fromisoformat(task['started_at']).strftime("%Y-%m-%d %H:%M")
                st.text(f"Started: {started}")
                
                if task['completed_at']:
                    completed = datetime.fromisoformat(task['completed_at']).strftime("%Y-%m-%d %H:%M")
                    st.text(f"Completed: {completed}")
            
            if task['error']:
                st.error(f"Error: {task['error']}")


def check_api_health():
    """Check API health status."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def start_generation(request_data):
    """Start repository generation."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=request_data,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def monitor_generation(task_id):
    """Monitor generation progress."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while True:
        try:
            response = requests.get(f"{API_BASE_URL}/status/{task_id}", timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                
                progress = status_data["progress"]
                status = status_data["status"]
                message = status_data["message"]
                
                progress_bar.progress(progress)
                status_text.text(f"Status: {status} - {message}")
                
                if status in ["completed", "failed"]:
                    break
                
                time.sleep(2)
            else:
                st.error("Failed to get generation status")
                break
        except requests.RequestException:
            st.error("Connection error while monitoring generation")
            break
    
    # Show final result
    if status == "completed":
        st.success("🎉 Generation completed successfully!")
        
        result = status_data.get("result", {})
        
        if result:
            st.subheader("📁 Generated Files")
            
            generated_files = result.get("generated_files", [])
            for file_path in generated_files:
                st.text(f"✅ {file_path}")
            
            execution_time = result.get("execution_time", 0)
            st.info(f"⏱️ Generation completed in {execution_time:.2f} seconds")
            
            # Download link
            if "download_url" in result:
                st.markdown(f"[📥 Download Project]({API_BASE_URL}{result['download_url']})")
    else:
        st.error("❌ Generation failed")
        error = status_data.get("error", "Unknown error")
        st.error(f"Error: {error}")


def load_projects():
    """Load all generated projects."""
    try:
        response = requests.get(f"{API_BASE_URL}/projects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("projects", [])
        return []
    except requests.RequestException:
        return []


def load_generation_tasks():
    """Load all generation tasks."""
    try:
        response = requests.get(f"{API_BASE_URL}/tasks", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("tasks", [])
        return []
    except requests.RequestException:
        return []


def download_project(project_name):
    """Download a project."""
    try:
        response = requests.get(f"{API_BASE_URL}/projects/{project_name}/download", timeout=30)
        if response.status_code == 200:
            st.success(f"✅ Project {project_name} downloaded successfully!")
        else:
            st.error(f"❌ Failed to download project {project_name}")
    except requests.RequestException:
        st.error(f"❌ Connection error while downloading {project_name}")


def show_project_info(project):
    """Show detailed project information."""
    st.json(project)


def delete_project(project_name):
    """Delete a project."""
    try:
        response = requests.delete(f"{API_BASE_URL}/projects/{project_name}", timeout=10)
        if response.status_code == 200:
            st.success(f"✅ Project {project_name} deleted successfully!")
            st.experimental_rerun()
        else:
            st.error(f"❌ Failed to delete project {project_name}")
    except requests.RequestException:
        st.error(f"❌ Connection error while deleting {project_name}")


if __name__ == "__main__":
    main()