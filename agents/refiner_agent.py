"""
Refiner Agent - Refines and ensures consistency across all generated code.
"""

import re
import ast
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from planner import FileSpec


@dataclass
class CodeIssue:
    """Represents a code quality issue."""
    file_path: str
    line_number: int
    issue_type: str
    message: str
    suggestion: Optional[str] = None


class RefinerAgent:
    """Agent responsible for refining and ensuring code consistency."""
    
    def __init__(self):
        self.refinement_rules = {
            'python': self._refine_python_code,
            'javascript': self._refine_javascript_code,
            'jsx': self._refine_jsx_code,
            'sql': self._refine_sql_code,
            'css': self._refine_css_code,
            'json': self._refine_json_code,
            'markdown': self._refine_markdown_code,
        }
    
    def refine_code(self, file_spec: FileSpec, code: str, project_context: Dict) -> str:
        """Refine code for consistency and quality."""
        file_extension = self._get_file_extension(file_spec.path)
        
        if file_extension in self.refinement_rules:
            refiner = self.refinement_rules[file_extension]
            return refiner(code, file_spec, project_context)
        else:
            return self._refine_generic_code(code, file_spec, project_context)
    
    def analyze_code_quality(self, files: Dict[str, str]) -> List[CodeIssue]:
        """Analyze code quality across all files."""
        issues = []
        
        for file_path, content in files.items():
            file_extension = self._get_file_extension(file_path)
            
            if file_extension == 'python':
                issues.extend(self._analyze_python_code(file_path, content))
            elif file_extension in ['javascript', 'jsx']:
                issues.extend(self._analyze_javascript_code(file_path, content))
            elif file_extension == 'sql':
                issues.extend(self._analyze_sql_code(file_path, content))
        
        return issues
    
    def ensure_consistency(self, files: Dict[str, str], project_context: Dict) -> Dict[str, str]:
        """Ensure consistency across all generated files."""
        refined_files = {}
        
        # First pass: individual file refinement
        for file_path, content in files.items():
            file_spec = FileSpec(
                path=file_path,
                type=None,
                agent="refiner_agent",
                dependencies=[],
                description=f"Refining {file_path}"
            )
            refined_files[file_path] = self.refine_code(file_spec, content, project_context)
        
        # Second pass: cross-file consistency
        refined_files = self._ensure_cross_file_consistency(refined_files, project_context)
        
        return refined_files
    
    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension for determining refinement strategy."""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.js'):
            return 'javascript'
        elif file_path.endswith('.jsx'):
            return 'jsx'
        elif file_path.endswith('.sql'):
            return 'sql'
        elif file_path.endswith('.css'):
            return 'css'
        elif file_path.endswith('.json'):
            return 'json'
        elif file_path.endswith('.md'):
            return 'markdown'
        else:
            return 'generic'
    
    def _refine_python_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine Python code for quality and consistency."""
        lines = code.split('\n')
        refined_lines = []
        
        for i, line in enumerate(lines):
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Ensure consistent indentation (4 spaces)
            if line.startswith('\t'):
                line = line.replace('\t', '    ')
            
            # Fix common formatting issues
            line = self._fix_python_formatting(line)
            
            refined_lines.append(line)
        
        # Join lines and ensure proper spacing
        refined_code = '\n'.join(refined_lines)
        
        # Ensure imports are properly organized
        refined_code = self._organize_python_imports(refined_code)
        
        # Add proper docstrings where missing
        refined_code = self._add_missing_docstrings(refined_code)
        
        return refined_code
    
    def _fix_python_formatting(self, line: str) -> str:
        """Fix common Python formatting issues."""
        # Fix spacing around operators
        line = re.sub(r'(\w+)=(\w+)', r'\1 = \2', line)
        line = re.sub(r'(\w+)==(\w+)', r'\1 == \2', line)
        line = re.sub(r'(\w+)!=(\w+)', r'\1 != \2', line)
        
        # Fix spacing after commas
        line = re.sub(r',(\w)', r', \1', line)
        
        # Fix spacing around colons in dictionaries
        line = re.sub(r'(\w+):(\w+)', r'\1: \2', line)
        
        return line
    
    def _organize_python_imports(self, code: str) -> str:
        """Organize Python imports according to PEP 8."""
        lines = code.split('\n')
        import_lines = []
        from_lines = []
        other_lines = []
        
        in_imports = True
        
        for line in lines:
            if line.strip().startswith('import ') and in_imports:
                import_lines.append(line)
            elif line.strip().startswith('from ') and in_imports:
                from_lines.append(line)
            elif line.strip() == '' and in_imports:
                continue
            else:
                in_imports = False
                other_lines.append(line)
        
        # Sort imports
        import_lines.sort()
        from_lines.sort()
        
        # Combine all lines
        organized_lines = []
        if import_lines:
            organized_lines.extend(import_lines)
        if from_lines:
            if import_lines:
                organized_lines.append('')
            organized_lines.extend(from_lines)
        if other_lines:
            if import_lines or from_lines:
                organized_lines.append('')
            organized_lines.extend(other_lines)
        
        return '\n'.join(organized_lines)
    
    def _add_missing_docstrings(self, code: str) -> str:
        """Add missing docstrings to Python functions and classes."""
        try:
            tree = ast.parse(code)
            # TODO: Implement AST-based docstring addition
            return code
        except SyntaxError:
            return code
    
    def _refine_javascript_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine JavaScript code for quality and consistency."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Ensure consistent indentation (2 spaces for JS)
            if line.startswith('\t'):
                line = line.replace('\t', '  ')
            
            # Fix common formatting issues
            line = self._fix_javascript_formatting(line)
            
            refined_lines.append(line)
        
        refined_code = '\n'.join(refined_lines)
        
        # Ensure proper semicolon usage
        refined_code = self._fix_javascript_semicolons(refined_code)
        
        return refined_code
    
    def _fix_javascript_formatting(self, line: str) -> str:
        """Fix common JavaScript formatting issues."""
        # Fix spacing around operators
        line = re.sub(r'(\w+)=([^=])', r'\1 = \2', line)
        line = re.sub(r'(\w+)==([^=])', r'\1 == \2', line)
        line = re.sub(r'(\w+)===([^=])', r'\1 === \2', line)
        
        # Fix spacing after commas
        line = re.sub(r',([^\s])', r', \1', line)
        
        # Fix spacing around colons in objects
        line = re.sub(r'(\w+):([^\s])', r'\1: \2', line)
        
        return line
    
    def _fix_javascript_semicolons(self, code: str) -> str:
        """Fix JavaScript semicolon usage."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Add semicolons to statements that need them
            if (stripped and 
                not stripped.endswith(';') and 
                not stripped.endswith('{') and 
                not stripped.endswith('}') and
                not stripped.startswith('//') and
                not stripped.startswith('/*') and
                not stripped.startswith('*') and
                not stripped.startswith('if') and
                not stripped.startswith('for') and
                not stripped.startswith('while') and
                not stripped.startswith('switch') and
                not stripped.startswith('function') and
                not stripped.startswith('class') and
                not stripped.startswith('import') and
                not stripped.startswith('export')):
                
                line = line.rstrip() + ';'
            
            refined_lines.append(line)
        
        return '\n'.join(refined_lines)
    
    def _refine_jsx_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine JSX code for quality and consistency."""
        # First apply JavaScript refinements
        refined_code = self._refine_javascript_code(code, file_spec, project_context)
        
        # Then apply JSX-specific refinements
        refined_code = self._fix_jsx_formatting(refined_code)
        
        return refined_code
    
    def _fix_jsx_formatting(self, code: str) -> str:
        """Fix JSX-specific formatting issues."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            # Fix JSX attribute formatting
            line = re.sub(r'(\w+)=([^{\s])', r'\1="\2"', line)
            
            # Fix JSX closing tag spacing
            line = re.sub(r'<\/(\w+)>', r'<\/\1>', line)
            
            refined_lines.append(line)
        
        return '\n'.join(refined_lines)
    
    def _refine_sql_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine SQL code for quality and consistency."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Ensure consistent SQL keyword casing
            line = self._fix_sql_keywords(line)
            
            refined_lines.append(line)
        
        return '\n'.join(refined_lines)
    
    def _fix_sql_keywords(self, line: str) -> str:
        """Fix SQL keyword casing."""
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
            'NOT', 'NULL', 'DEFAULT', 'UNIQUE', 'CHECK', 'CONSTRAINT', 'AND', 'OR',
            'ORDER', 'BY', 'GROUP', 'HAVING', 'INNER', 'LEFT', 'RIGHT', 'FULL',
            'OUTER', 'JOIN', 'ON', 'AS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'
        ]
        
        for keyword in sql_keywords:
            pattern = r'\b' + keyword.lower() + r'\b'
            line = re.sub(pattern, keyword, line, flags=re.IGNORECASE)
        
        return line
    
    def _refine_css_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine CSS code for quality and consistency."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Fix CSS property formatting
            line = self._fix_css_properties(line)
            
            refined_lines.append(line)
        
        return '\n'.join(refined_lines)
    
    def _fix_css_properties(self, line: str) -> str:
        """Fix CSS property formatting."""
        # Fix spacing around colons
        line = re.sub(r'(\w+):([^\s])', r'\1: \2', line)
        
        # Fix spacing after semicolons
        line = re.sub(r';([^\s}])', r'; \1', line)
        
        return line
    
    def _refine_json_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine JSON code for quality and consistency."""
        try:
            import json
            # Parse and reformat JSON
            data = json.loads(code)
            return json.dumps(data, indent=2, sort_keys=True)
        except json.JSONDecodeError:
            return code
    
    def _refine_markdown_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine Markdown code for quality and consistency."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Fix Markdown formatting
            line = self._fix_markdown_formatting(line)
            
            refined_lines.append(line)
        
        return '\n'.join(refined_lines)
    
    def _fix_markdown_formatting(self, line: str) -> str:
        """Fix Markdown formatting issues."""
        # Fix spacing around headers
        line = re.sub(r'^(#+)([^\s])', r'\1 \2', line)
        
        # Fix list formatting
        line = re.sub(r'^(\s*)-([^\s])', r'\1- \2', line)
        line = re.sub(r'^(\s*)\*([^\s])', r'\1* \2', line)
        
        return line
    
    def _refine_generic_code(self, code: str, file_spec: FileSpec, project_context: Dict) -> str:
        """Refine generic code files."""
        lines = code.split('\n')
        refined_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            refined_lines.append(line)
        
        return '\n'.join(refined_lines)
    
    def _ensure_cross_file_consistency(self, files: Dict[str, str], project_context: Dict) -> Dict[str, str]:
        """Ensure consistency across all files."""
        # Extract project information
        project_name = project_context.get('project_name', 'MyApp')
        
        # Update all files with consistent project name
        refined_files = {}
        for file_path, content in files.items():
            # Replace placeholder project names
            content = content.replace('MyApp', project_name)
            content = content.replace('my-app', project_name.lower().replace('_', '-'))
            content = content.replace('my_app', project_name.lower())
            
            refined_files[file_path] = content
        
        return refined_files
    
    def _analyze_python_code(self, file_path: str, code: str) -> List[CodeIssue]:
        """Analyze Python code for issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for long lines
            if len(line) > 88:
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type='line_length',
                    message=f'Line too long ({len(line)} > 88 characters)',
                    suggestion='Consider breaking long lines'
                ))
            
            # Check for missing docstrings
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                if i < len(lines) and not lines[i].strip().startswith('"""'):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type='missing_docstring',
                        message='Missing docstring',
                        suggestion='Add docstring to describe the function/class'
                    ))
        
        return issues
    
    def _analyze_javascript_code(self, file_path: str, code: str) -> List[CodeIssue]:
        """Analyze JavaScript code for issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for console.log statements
            if 'console.log' in line and not line.strip().startswith('//'):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type='console_log',
                    message='Console.log statement found',
                    suggestion='Remove console.log statements in production code'
                ))
            
            # Check for missing semicolons
            stripped = line.strip()
            if (stripped and 
                not stripped.endswith(';') and 
                not stripped.endswith('{') and 
                not stripped.endswith('}') and
                not stripped.startswith('//') and
                not stripped.startswith('if') and
                not stripped.startswith('for') and
                not stripped.startswith('while')):
                
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=i,
                    issue_type='missing_semicolon',
                    message='Missing semicolon',
                    suggestion='Add semicolon at end of statement'
                ))
        
        return issues
    
    def _analyze_sql_code(self, file_path: str, code: str) -> List[CodeIssue]:
        """Analyze SQL code for issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for SQL injection risks
            if 'WHERE' in line.upper() and ('=' in line or 'LIKE' in line.upper()):
                if not ('$' in line or '?' in line):
                    issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=i,
                        issue_type='sql_injection_risk',
                        message='Potential SQL injection risk',
                        suggestion='Use parameterized queries'
                    ))
        
        return issues
    
    def generate_code_quality_report(self, files: Dict[str, str]) -> str:
        """Generate a code quality report."""
        issues = self.analyze_code_quality(files)
        
        report_lines = [
            "# Code Quality Report",
            "",
            f"Total files analyzed: {len(files)}",
            f"Total issues found: {len(issues)}",
            ""
        ]
        
        if issues:
            report_lines.append("## Issues Found:")
            report_lines.append("")
            
            for issue in issues:
                report_lines.append(f"### {issue.file_path}:{issue.line_number}")
                report_lines.append(f"**Type:** {issue.issue_type}")
                report_lines.append(f"**Message:** {issue.message}")
                if issue.suggestion:
                    report_lines.append(f"**Suggestion:** {issue.suggestion}")
                report_lines.append("")
        else:
            report_lines.append("## No issues found! 🎉")
        
        return "\n".join(report_lines)