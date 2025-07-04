"""
Frontend Agent - Generates UI code for various frontend frameworks.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from agents.types import FileSpec, TechStack
from agents.llm_utils import generate_code_with_llm


@dataclass
class ComponentSpec:
    """Specification for a UI component."""
    name: str
    props: Dict
    children: List[str]
    styles: Dict
    functionality: List[str]


class FrontendAgent:
    """Agent responsible for generating frontend code."""
    
    def __init__(self):
        self.supported_frameworks = {
            TechStack.REACT: self._generate_react_code,
            TechStack.VUE: self._generate_vue_code,
            TechStack.ANGULAR: self._generate_angular_code,
            TechStack.FLUTTER: self._generate_flutter_code,
        }
    
    def generate_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate frontend code for a specific file."""
        if file_spec.tech_stack not in self.supported_frameworks:
            raise ValueError(f"Unsupported frontend framework: {file_spec.tech_stack}")
        
        generator = self.supported_frameworks[file_spec.tech_stack]
        return generator(file_spec, project_context)
    
    def _generate_react_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate React component code."""
        file_name = file_spec.path.split('/')[-1]
        
        if file_name == 'App.jsx':
            return self._generate_react_app(project_context)
        elif file_name == 'package.json':
            return self._generate_react_package_json(project_context)
        elif file_name.endswith('.jsx'):
            component_name = file_name.replace('.jsx', '')
            return self._generate_react_component(component_name, project_context)
        else:
            return self._generate_react_generic_file(file_spec, project_context)
    
    def _generate_react_app(self, project_context: Dict) -> str:
        """Generate main React App component."""
        features = project_context.get('features', [])
        has_auth = 'authentication' in features
        has_routing = True  # Always include routing
        
        imports = [
            "import React from 'react';",
            "import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';",
            "import Header from './components/Header';",
            "import Home from './pages/Home';",
            "import './App.css';"
        ]
        
        if has_auth:
            imports.extend([
                "import Login from './pages/Login';",
                "import Register from './pages/Register';"
            ])
        
        routes = [
            "          <Route path=\"/\" element={<Home />} />"
        ]
        
        if has_auth:
            routes.extend([
                "          <Route path=\"/login\" element={<Login />} />",
                "          <Route path=\"/register\" element={<Register />} />"
            ])
        
        return f"""
{chr(10).join(imports)}

function App() {{
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
{chr(10).join(routes)}
          </Routes>
        </main>
      </div>
    </Router>
  );
}}

export default App;
""".strip()
    
    def _generate_react_component(self, component_name: str, project_context: Dict) -> str:
        """Generate a React component."""
        features = project_context.get('features', [])
        
        if component_name == 'Header':
            return self._generate_header_component(project_context)
        elif component_name == 'Home':
            return self._generate_home_page(project_context)
        elif component_name == 'Login':
            return self._generate_login_page(project_context)
        elif component_name == 'Register':
            return self._generate_register_page(project_context)
        else:
            return self._generate_generic_component(component_name, project_context)
    
    def _generate_header_component(self, project_context: Dict) -> str:
        """Generate header component."""
        features = project_context.get('features', [])
        has_auth = 'authentication' in features
        
        auth_links = ""
        if has_auth:
            auth_links = """
          <div className="auth-links">
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="nav-link">Register</Link>
          </div>"""
        
        return f"""
import React from 'react';
import {{ Link }} from 'react-router-dom';
import './Header.css';

const Header = () => {{
  return (
    <header className="header">
      <div className="container">
        <div className="logo">
          <Link to="/" className="logo-link">
            {project_context.get('project_name', 'MyApp')}
          </Link>
        </div>
        <nav className="nav">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/about" className="nav-link">About</Link>
          <Link to="/contact" className="nav-link">Contact</Link>{auth_links}
        </nav>
      </div>
    </header>
  );
}};

export default Header;
""".strip()
    
    def _generate_home_page(self, project_context: Dict) -> str:
        """Generate home page component."""
        project_name = project_context.get('project_name', 'MyApp')
        features = project_context.get('features', [])
        
        feature_sections = []
        if 'task_management' in features:
            feature_sections.append("""
        <section className="feature-section">
          <h2>Task Management</h2>
          <p>Organize your tasks efficiently with our intuitive task management system.</p>
        </section>""")
        
        if 'real_time' in features:
            feature_sections.append("""
        <section className="feature-section">
          <h2>Real-time Updates</h2>
          <p>Stay synchronized with real-time updates across all your devices.</p>
        </section>""")
        
        if 'file_upload' in features:
            feature_sections.append("""
        <section className="feature-section">
          <h2>File Management</h2>
          <p>Upload, organize, and share files seamlessly within the platform.</p>
        </section>""")
        
        features_html = ''.join(feature_sections) if feature_sections else """
        <section className="feature-section">
          <h2>Welcome</h2>
          <p>Discover the power of our application and boost your productivity.</p>
        </section>"""
        
        return f"""
import React from 'react';
import './Home.css';

const Home = () => {{
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1>Welcome to {project_name}</h1>
          <p>Your ultimate solution for modern web applications</p>
          <button className="cta-button">Get Started</button>
        </div>
      </section>
      
      <section className="features">
        <div className="container">{features_html}
        </div>
      </section>
    </div>
  );
}};

export default Home;
""".strip()
    
    def _generate_login_page(self, project_context: Dict) -> str:
        """Generate login page component."""
        return """
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement login logic
    console.log('Login attempt:', formData);
  };

  return (
    <div className="login">
      <div className="login-container">
        <div className="login-form">
          <h2>Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit" className="login-button">Login</button>
          </form>
          <p className="signup-link">
            Don't have an account? <Link to="/register">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
""".strip()
    
    def _generate_register_page(self, project_context: Dict) -> str:
        """Generate register page component."""
        return """
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Register.css';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    // TODO: Implement registration logic
    console.log('Registration attempt:', formData);
  };

  return (
    <div className="register">
      <div className="register-container">
        <div className="register-form">
          <h2>Create Account</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit" className="register-button">Create Account</button>
          </form>
          <p className="login-link">
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
""".strip()
    
    def _generate_generic_component(self, component_name: str, project_context: Dict) -> str:
        """Generate a generic React component."""
        return f"""
import React from 'react';
import './{component_name}.css';

const {component_name} = () => {{
  return (
    <div className="{component_name.lower()}">
      <h2>{component_name}</h2>
      <p>This is the {component_name} component.</p>
    </div>
  );
}};

export default {component_name};
""".strip()
    
    def _generate_react_package_json(self, project_context: Dict) -> str:
        """Generate package.json for React project."""
        project_name = project_context.get('project_name', 'my-app')
        features = project_context.get('features', [])
        
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.8.0",
            "react-scripts": "5.0.1"
        }
        
        # Add feature-specific dependencies
        if 'real_time' in features:
            dependencies["socket.io-client"] = "^4.7.2"
        
        if 'file_upload' in features:
            dependencies["axios"] = "^1.4.0"
        
        if 'authentication' in features:
            dependencies["jwt-decode"] = "^3.1.2"
        
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "private": True,
            "dependencies": dependencies,
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        return json.dumps(package_json, indent=2)
    
    def _generate_react_generic_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate a generic React file."""
        if file_spec.path.endswith('.css'):
            return self._generate_css_file(file_spec, project_context)
        elif file_spec.path.endswith('.js') or file_spec.path.endswith('.jsx'):
            return self._generate_js_file(file_spec, project_context)
        else:
            return f"// Generated file: {file_spec.path}\n// TODO: Implement {file_spec.description}"
    
    def _generate_css_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate CSS file."""
        file_name = file_spec.path.split('/')[-1].replace('.css', '')
        
        if file_name == 'App':
            return """
.App {
  text-align: center;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
""".strip()
        
        elif file_name == 'Header':
            return """
.header {
  background-color: #282c34;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-link {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(255,255,255,0.1);
}

.auth-links {
  display: flex;
  gap: 1rem;
}
""".strip()
        
        else:
            return f"""
.{file_name.lower()} {{
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}}

.{file_name.lower()} h2 {{
  color: #333;
  margin-bottom: 1rem;
}}

.{file_name.lower()} p {{
  color: #666;
  line-height: 1.6;
}}
""".strip()
    
    def _generate_js_file(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate JavaScript file."""
        return f"""
// {file_spec.description}
// TODO: Implement functionality for {file_spec.path}

export default {{}};
""".strip()
    
    def _generate_vue_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate Vue.js code."""
        # TODO: Implement Vue.js code generation
        return f"""
<template>
  <div class="vue-component">
    <h2>Vue Component</h2>
    <p>Generated Vue.js component for {file_spec.path}</p>
  </div>
</template>

<script>
export default {{
  name: 'VueComponent',
  data() {{
    return {{
      // component data
    }};
  }}
}};
</script>

<style scoped>
.vue-component {{
  padding: 20px;
}}
</style>
""".strip()
    
    def _generate_angular_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate Angular code."""
        # TODO: Implement Angular code generation
        return f"""
import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-component',
  template: `
    <div class="angular-component">
      <h2>Angular Component</h2>
      <p>Generated Angular component for {file_spec.path}</p>
    </div>
  `,
  styles: [`
    .angular-component {{
      padding: 20px;
    }}
  `]
}})
export class AppComponent {{
  title = 'Angular Component';
}}
""".strip()
    
    def _generate_flutter_code(self, file_spec: FileSpec, project_context: Dict) -> str:
        """Generate Flutter code."""
        # TODO: Implement Flutter code generation
        return f"""
import 'package:flutter/material.dart';

class FlutterWidget extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text('Flutter Widget'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Generated Flutter widget for {file_spec.path}',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
    );
  }}
}}
""".strip()

class MistralFrontendAgent:
    """Frontend agent using Mistral/CodeGemma LLM."""
    def generate_file(self, file_spec, project_context):
        prompt = f"Generate the frontend file {file_spec.path} for the following project context: {project_context}"
        code = generate_code_with_llm(
            prompt,
            agent_name='frontend_agent',
            max_new_tokens=1024,
            temperature=0.2
        )
        return code