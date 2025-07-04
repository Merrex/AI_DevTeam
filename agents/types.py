from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TechStack(Enum):
    REACT = "react"
    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    NODEJS = "nodejs"
    VUE = "vue"
    ANGULAR = "angular"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    FLUTTER = "flutter"
    # Add more as needed

@dataclass
class FileSpec:
    path: str
    type: Optional[str]
    agent: str
    dependencies: List[str]
    description: str
    priority: int = 1
    tech_stack: Optional[str] = None 