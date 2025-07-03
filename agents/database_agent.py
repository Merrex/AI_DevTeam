"""
Database Agent - Generates database schemas, models, and queries.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from planner import FileSpec, TechStack


@dataclass
class TableSpec:
    """Specification for a database table."""
    name: str
    columns: List[Dict]
    indexes: List[str]
    relationships: List[Dict]
    constraints: List[str]


class DatabaseAgent:
    """Agent responsible for generating database code."""
    
    def __init__(self):
        self.supported_databases = {
            TechStack.POSTGRESQL: self._generate_postgresql_code,
            TechStack.MYSQL: self._generate_mysql_code,
            TechStack.MONGODB: self._generate_mongodb_code,
            TechStack.SQLITE: self._generate_sqlite_code,
        }
    
    def generate_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate database code for a specific file."""
        db_tech = project_context.get('tech_stack', {}).get('database', TechStack.POSTGRESQL)
        
        if db_tech not in self.supported_databases:
            raise ValueError(f"Unsupported database: {db_tech}")
        
        generator = self.supported_databases[db_tech]
        return generator(file_spec, project_context)
    
    def _generate_postgresql_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate PostgreSQL database code."""
        file_name = file_spec.path.split('/')[-1]
        
        if file_name == 'schema.sql':
            return self._generate_postgresql_schema(project_context)
        elif 'migration' in file_name:
            return self._generate_postgresql_migration(file_spec, project_context)
        else:
            return self._generate_postgresql_generic_file(file_spec, project_context)
    
    def _generate_postgresql_schema(self, project_context: Dict) -> str:
        """Generate PostgreSQL schema."""
        features = project_context.get('features', [])
        project_name = project_context.get('project_name', 'app')
        
        schema_parts = [
            "-- Database Schema",
            f"-- Generated for {project_name}",
            "",
            "-- Enable UUID extension",
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            ""
        ]
        
        # Users table (always included if authentication is needed)
        if 'authentication' in features:
            schema_parts.extend([
                "-- Users table",
                "CREATE TABLE IF NOT EXISTS users (",
                "    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
                "    email VARCHAR(255) UNIQUE NOT NULL,",
                "    name VARCHAR(255) NOT NULL,",
                "    hashed_password VARCHAR(255) NOT NULL,",
                "    is_active BOOLEAN DEFAULT TRUE,",
                "    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,",
                "    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                ");",
                "",
                "-- Indexes for users table",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);",
                ""
            ])
        
        # Task management tables
        if 'task_management' in features:
            schema_parts.extend([
                "-- Tasks table",
                "CREATE TABLE IF NOT EXISTS tasks (",
                "    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
                "    title VARCHAR(255) NOT NULL,",
                "    description TEXT,",
                "    status VARCHAR(50) DEFAULT 'pending',",
                "    priority VARCHAR(50) DEFAULT 'medium',",
                "    due_date TIMESTAMP WITH TIME ZONE,",
                "    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,",
                "    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
            ])
            
            if 'authentication' in features:
                schema_parts.extend([
                    "    user_id UUID REFERENCES users(id) ON DELETE CASCADE"
                ])
            
            schema_parts.extend([
                ");",
                "",
                "-- Indexes for tasks table",
                "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);",
                "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);",
                "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);"
            ])
            
            if 'authentication' in features:
                schema_parts.append("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);")
            
            schema_parts.append("")
        
        # E-commerce tables
        if 'e_commerce' in features:
            schema_parts.extend([
                "-- Products table",
                "CREATE TABLE IF NOT EXISTS products (",
                "    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
                "    name VARCHAR(255) NOT NULL,",
                "    description TEXT,",
                "    price DECIMAL(10, 2) NOT NULL,",
                "    stock_quantity INTEGER DEFAULT 0,",
                "    category VARCHAR(100),",
                "    image_url VARCHAR(500),",
                "    is_active BOOLEAN DEFAULT TRUE,",
                "    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,",
                "    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
                ");",
                "",
                "-- Orders table",
                "CREATE TABLE IF NOT EXISTS orders (",
                "    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
                "    total_amount DECIMAL(10, 2) NOT NULL,",
                "    status VARCHAR(50) DEFAULT 'pending',",
                "    shipping_address TEXT,",
                "    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,",
                "    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
            ])
            
            if 'authentication' in features:
                schema_parts.append("    user_id UUID REFERENCES users(id) ON DELETE CASCADE")
            
            schema_parts.extend([
                ");",
                "",
                "-- Order items table",
                "CREATE TABLE IF NOT EXISTS order_items (",
                "    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
                "    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,",
                "    product_id UUID REFERENCES products(id) ON DELETE CASCADE,",
                "    quantity INTEGER NOT NULL,",
                "    price DECIMAL(10, 2) NOT NULL",
                ");",
                ""
            ])
        
        # File uploads table
        if 'file_upload' in features:
            schema_parts.extend([
                "-- Files table",
                "CREATE TABLE IF NOT EXISTS files (",
                "    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),",
                "    filename VARCHAR(255) NOT NULL,",
                "    original_name VARCHAR(255) NOT NULL,",
                "    file_size INTEGER NOT NULL,",
                "    mime_type VARCHAR(100),",
                "    file_path VARCHAR(500) NOT NULL,",
                "    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
            ])
            
            if 'authentication' in features:
                schema_parts.append("    user_id UUID REFERENCES users(id) ON DELETE CASCADE")
            
            schema_parts.extend([
                ");",
                ""
            ])
        
        # Trigger function for updated_at
        schema_parts.extend([
            "-- Function to update updated_at timestamp",
            "CREATE OR REPLACE FUNCTION update_updated_at_column()",
            "RETURNS TRIGGER AS $$",
            "BEGIN",
            "    NEW.updated_at = CURRENT_TIMESTAMP;",
            "    RETURN NEW;",
            "END;",
            "$$ language 'plpgsql';",
            ""
        ])
        
        # Apply triggers to tables with updated_at column
        tables_with_updated_at = []
        if 'authentication' in features:
            tables_with_updated_at.append('users')
        if 'task_management' in features:
            tables_with_updated_at.append('tasks')
        if 'e_commerce' in features:
            tables_with_updated_at.extend(['products', 'orders'])
        
        for table in tables_with_updated_at:
            schema_parts.extend([
                f"-- Trigger for {table} table",
                f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};",
                f"CREATE TRIGGER update_{table}_updated_at",
                f"    BEFORE UPDATE ON {table}",
                f"    FOR EACH ROW",
                f"    EXECUTE FUNCTION update_updated_at_column();",
                ""
            ])
        
        return "\n".join(schema_parts)
    
    def _generate_postgresql_migration(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate PostgreSQL migration file."""
        migration_name = file_spec.path.split('/')[-1].replace('.sql', '')
        
        return f"""
-- Migration: {migration_name}
-- Generated migration file

-- Add your migration SQL here
-- This is a placeholder migration

-- Example:
-- ALTER TABLE users ADD COLUMN phone VARCHAR(20);
-- CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- Remember to add corresponding rollback SQL as comments:
-- ROLLBACK SQL:
-- ALTER TABLE users DROP COLUMN phone;
-- DROP INDEX IF EXISTS idx_users_phone;
""".strip()
    
    def _generate_postgresql_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate generic PostgreSQL file."""
        return f"""
-- {file_spec.description}
-- Generated PostgreSQL file: {file_spec.path}

-- TODO: Implement {file_spec.description}
""".strip()
    
    def _generate_mysql_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate MySQL database code."""
        file_name = file_spec.path.split('/')[-1]
        
        if file_name == 'schema.sql':
            return self._generate_mysql_schema(project_context)
        else:
            return self._generate_mysql_generic_file(file_spec, project_context)
    
    def _generate_mysql_schema(self, project_context: Dict) -> str:
        """Generate MySQL schema."""
        features = project_context.get('features', [])
        project_name = project_context.get('project_name', 'app')
        
        schema_parts = [
            "-- Database Schema",
            f"-- Generated for {project_name}",
            "",
            "-- Set charset and collation",
            "SET NAMES utf8mb4;",
            "SET FOREIGN_KEY_CHECKS = 0;",
            ""
        ]
        
        # Users table
        if 'authentication' in features:
            schema_parts.extend([
                "-- Users table",
                "CREATE TABLE IF NOT EXISTS `users` (",
                "    `id` INT AUTO_INCREMENT PRIMARY KEY,",
                "    `email` VARCHAR(255) UNIQUE NOT NULL,",
                "    `name` VARCHAR(255) NOT NULL,",
                "    `hashed_password` VARCHAR(255) NOT NULL,",
                "    `is_active` BOOLEAN DEFAULT TRUE,",
                "    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
                "    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                "",
                "-- Indexes for users table",
                "CREATE INDEX `idx_users_email` ON `users`(`email`);",
                ""
            ])
        
        schema_parts.append("SET FOREIGN_KEY_CHECKS = 1;")
        
        return "\n".join(schema_parts)
    
    def _generate_mysql_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate generic MySQL file."""
        return f"""
-- {file_spec.description}
-- Generated MySQL file: {file_spec.path}

-- TODO: Implement {file_spec.description}
""".strip()
    
    def _generate_mongodb_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate MongoDB database code."""
        file_name = file_spec.path.split('/')[-1]
        
        if file_name == 'schema.js':
            return self._generate_mongodb_schema(project_context)
        else:
            return self._generate_mongodb_generic_file(file_spec, project_context)
    
    def _generate_mongodb_schema(self, project_context: Dict) -> str:
        """Generate MongoDB schema."""
        features = project_context.get('features', [])
        project_name = project_context.get('project_name', 'app')
        
        schema_parts = [
            "// Database Schema",
            f"// Generated for {project_name}",
            "",
            "// MongoDB Collections and Indexes",
            ""
        ]
        
        if 'authentication' in features:
            schema_parts.extend([
                "// Users collection",
                "db.users.createIndex({ email: 1 }, { unique: true });",
                "db.users.createIndex({ created_at: 1 });",
                "",
                "// Example user document structure:",
                "// {",
                "//   _id: ObjectId(),",
                "//   email: 'user@example.com',",
                "//   name: 'John Doe',",
                "//   hashedPassword: 'hashed_password_here',",
                "//   isActive: true,",
                "//   createdAt: new Date(),",
                "//   updatedAt: new Date()",
                "// }",
                ""
            ])
        
        return "\n".join(schema_parts)
    
    def _generate_mongodb_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate generic MongoDB file."""
        return f"""
// {file_spec.description}
// Generated MongoDB file: {file_spec.path}

// TODO: Implement {file_spec.description}
""".strip()
    
    def _generate_sqlite_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate SQLite database code."""
        file_name = file_spec.path.split('/')[-1]
        
        if file_name == 'schema.sql':
            return self._generate_sqlite_schema(project_context)
        else:
            return self._generate_sqlite_generic_file(file_spec, project_context)
    
    def _generate_sqlite_schema(self, project_context: Dict) -> str:
        """Generate SQLite schema."""
        features = project_context.get('features', [])
        project_name = project_context.get('project_name', 'app')
        
        schema_parts = [
            "-- Database Schema",
            f"-- Generated for {project_name}",
            "",
            "-- SQLite Schema",
            "PRAGMA foreign_keys = ON;",
            ""
        ]
        
        if 'authentication' in features:
            schema_parts.extend([
                "-- Users table",
                "CREATE TABLE IF NOT EXISTS users (",
                "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
                "    email TEXT UNIQUE NOT NULL,",
                "    name TEXT NOT NULL,",
                "    hashed_password TEXT NOT NULL,",
                "    is_active BOOLEAN DEFAULT 1,",
                "    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,",
                "    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP",
                ");",
                "",
                "-- Indexes for users table",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
                "",
                "-- Trigger for updating updated_at",
                "CREATE TRIGGER IF NOT EXISTS update_users_updated_at",
                "    AFTER UPDATE ON users",
                "    FOR EACH ROW",
                "    BEGIN",
                "        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;",
                "    END;",
                ""
            ])
        
        return "\n".join(schema_parts)
    
    def _generate_sqlite_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate generic SQLite file."""
        return f"""
-- {file_spec.description}
-- Generated SQLite file: {file_spec.path}

-- TODO: Implement {file_spec.description}
""".strip()