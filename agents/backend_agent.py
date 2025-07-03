"""
Backend Agent - Generates API routes and services for various backend frameworks.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from planner import FileSpec, TechStack
import os
from agents.llm_utils import generate_code_with_llm


@dataclass
class APIEndpoint:
    """Specification for an API endpoint."""
    path: str
    method: str
    description: str
    parameters: Dict
    response_schema: Dict
    auth_required: bool = False


class BackendAgent:
    """Agent responsible for generating backend code."""
    
    def __init__(self):
        self.supported_frameworks = {
            TechStack.FASTAPI: self._generate_fastapi_code,
            TechStack.FLASK: self._generate_flask_code,
            TechStack.DJANGO: self._generate_django_code,
            TechStack.NODEJS: self._generate_nodejs_code,
        }
    
    def generate_file(self, file_spec: FileSpec, project_context: Dict, use_llm: bool = False) -> str:
        """Generate backend code for a specific file. If use_llm is True, use LLM for generation."""
        if use_llm:
            prompt = self._build_llm_prompt(file_spec, project_context)
            return generate_code_with_llm(prompt)
        if file_spec.tech_stack not in self.supported_frameworks:
            raise ValueError(f"Unsupported backend framework: {file_spec.tech_stack}")
        generator = self.supported_frameworks[file_spec.tech_stack]
        return generator(file_spec, project_context)
    
    def _generate_fastapi_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate FastAPI code."""
        file_name = file_spec.path.split('/')[-1]
        
        if file_name == 'main.py':
            return self._generate_fastapi_main(project_context)
        elif file_name == 'requirements.txt':
            return self._generate_fastapi_requirements(project_context)
        elif file_name.startswith('auth.py'):
            return self._generate_fastapi_auth(project_context)
        elif file_name.startswith('user.py'):
            return self._generate_fastapi_user_model(project_context)
        elif 'router' in file_spec.path:
            return self._generate_fastapi_router(file_spec, project_context)
        else:
            return self._generate_fastapi_generic_file(file_spec, project_context)
    
    def _generate_fastapi_main(self, project_context: Dict) -> str:
        """Generate FastAPI main application."""
        features = project_context.get('features', [])
        has_auth = 'authentication' in features
        has_cors = True  # Always enable CORS for web apps
        
        imports = [
            "from fastapi import FastAPI, HTTPException, Depends",
            "from fastapi.middleware.cors import CORSMiddleware",
            "from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials",
            "import uvicorn"
        ]
        
        if has_auth:
            imports.append("from routers import auth")
        
        middleware_setup = """
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
""" if has_cors else ""
        
        router_includes = []
        if has_auth:
            router_includes.append("app.include_router(auth.router, prefix=\"/api/auth\", tags=[\"auth\"])")
        
        return f"""
{chr(10).join(imports)}

app = FastAPI(
    title="{project_context.get('project_name', 'API')}",
    description="Generated API using FastAPI",
    version="1.0.0"
)

{middleware_setup}

# Security
security = HTTPBearer()

@app.get("/")
async def root():
    return {{"message": "Welcome to {project_context.get('project_name', 'API')}"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}

{chr(10).join(router_includes)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
""".strip()
    
    def _generate_fastapi_requirements(self, project_context: Dict) -> str:
        """Generate requirements.txt for FastAPI."""
        features = project_context.get('features', [])
        integrations = project_context.get('integrations', [])
        
        requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "pydantic==2.5.0",
            "python-multipart==0.0.6"
        ]
        
        # Database dependencies
        db_tech = project_context.get('tech_stack', {}).get('database')
        if db_tech == TechStack.POSTGRESQL:
            requirements.extend([
                "sqlalchemy==2.0.23",
                "psycopg2-binary==2.9.9",
                "alembic==1.13.1"
            ])
        elif db_tech == TechStack.MONGODB:
            requirements.extend([
                "motor==3.3.2",
                "pymongo==4.6.0"
            ])
        elif db_tech == TechStack.MYSQL:
            requirements.extend([
                "sqlalchemy==2.0.23",
                "PyMySQL==1.1.0",
                "alembic==1.13.1"
            ])
        
        # Authentication dependencies
        if 'authentication' in features:
            requirements.extend([
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-multipart==0.0.6"
            ])
        
        # File upload dependencies
        if 'file_upload' in features:
            requirements.extend([
                "python-multipart==0.0.6",
                "pillow==10.1.0"
            ])
        
        # Integration dependencies
        if 'payment' in integrations:
            requirements.append("stripe==7.8.0")
        
        if 'email' in integrations:
            requirements.append("emails==0.6")
        
        return chr(10).join(sorted(requirements))
    
    def _generate_fastapi_auth(self, project_context: Dict) -> str:
        """Generate FastAPI authentication router."""
        return """
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

router = APIRouter()

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool = True

# Password hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # TODO: Get user from database
    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_user_by_email(email: str):
    # TODO: Implement database lookup
    # This is a placeholder - replace with actual database query
    return User(id=1, email=email, name="Test User")

def authenticate_user(email: str, password: str):
    # TODO: Implement user authentication
    # This is a placeholder - replace with actual database query
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    # TODO: Check if user already exists
    # TODO: Save user to database
    hashed_password = get_password_hash(user.password)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    authenticated_user = authenticate_user(user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
""".strip()
    
    def _generate_fastapi_user_model(self, project_context: Dict) -> str:
        """Generate FastAPI user model."""
        db_tech = project_context.get('tech_stack', {}).get('database')
        
        if db_tech == TechStack.POSTGRESQL:
            return """
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
""".strip()
        else:
            return """
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
""".strip()
    
    def _generate_fastapi_router(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate a FastAPI router file."""
        router_name = file_spec.path.split('/')[-1].replace('.py', '')
        
        return f"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class {router_name.title()}Base(BaseModel):
    # TODO: Define base model fields
    pass

class {router_name.title()}Create({router_name.title()}Base):
    # TODO: Define creation model fields
    pass

class {router_name.title()}Update(BaseModel):
    # TODO: Define update model fields
    pass

class {router_name.title()}Response({router_name.title()}Base):
    id: int
    # TODO: Add response model fields
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[{router_name.title()}Response])
async def get_{router_name}s():
    # TODO: Implement get all {router_name}s
    return []

@router.get("/{{item_id}}", response_model={router_name.title()}Response)
async def get_{router_name}(item_id: int):
    # TODO: Implement get {router_name} by ID
    raise HTTPException(status_code=404, detail="{router_name.title()} not found")

@router.post("/", response_model={router_name.title()}Response)
async def create_{router_name}(item: {router_name.title()}Create):
    # TODO: Implement create {router_name}
    pass

@router.put("/{{item_id}}", response_model={router_name.title()}Response)
async def update_{router_name}(item_id: int, item: {router_name.title()}Update):
    # TODO: Implement update {router_name}
    pass

@router.delete("/{{item_id}}")
async def delete_{router_name}(item_id: int):
    # TODO: Implement delete {router_name}
    pass
""".strip()
    
    def _generate_fastapi_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate a generic FastAPI file."""
        return f"""
# {file_spec.description}
# Generated file: {file_spec.path}

# TODO: Implement {file_spec.description}
""".strip()
    
    def _generate_flask_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate Flask code."""
        return f"""
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({{"message": "Welcome to {project_context.get('project_name', 'API')}"}})

@app.route('/health')
def health():
    return jsonify({{"status": "healthy"}})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
""".strip()
    
    def _generate_django_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate Django code."""
        # TODO: Implement Django code generation
        return f"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

class APIView(View):
    def get(self, request):
        return JsonResponse({{"message": "Welcome to {project_context.get('project_name', 'API')}"}})

def health_check(request):
    return JsonResponse({{"status": "healthy"}})
""".strip()
    
    def _generate_nodejs_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate Node.js code."""
        # TODO: Implement Node.js code generation
        return f"""
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {{
    res.json({{ message: 'Welcome to {project_context.get('project_name', 'API')}' }});
}});

app.get('/health', (req, res) => {{
    res.json({{ status: 'healthy' }});
}});

app.listen(PORT, () => {{
    console.log(`Server is running on port ${{PORT}}`);
}});
""".strip()

    def _build_llm_prompt(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Build a prompt for the LLM based on file spec and context."""
        return f"""
Generate the following backend file for a {project_context.get('tech_stack', {}).get('backend', 'backend')} project:
File path: {file_spec.path}
Description: {file_spec.description}
Project features: {project_context.get('features', [])}
Integrations: {project_context.get('integrations', [])}
Please provide the complete code for this file.
""".strip()