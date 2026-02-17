"""
Z3ube Code Generator - Advanced Multi-Language Code Generation

This module implements:
- General programming code generation (Python, JavaScript, C++, etc.)
- Specialized robotic engineering code (ROS2, Arduino, embedded)
- Automatic test generation
- Code analysis and optimization
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CPP = "cpp"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    # Robotics-specific
    ROS2_PYTHON = "ros2_python"
    ROS2_CPP = "ros2_cpp"
    ARDUINO = "arduino"
    MICROPYTHON = "micropython"


@dataclass
class CodeResult:
    """Generated code result"""
    language: str
    code: str
    tests: Optional[str] = None
    explanation: str = ""
    dependencies: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "code": self.code,
            "tests": self.tests,
            "explanation": self.explanation,
            "dependencies": self.dependencies,
            "quality_score": self.quality_score
        }


class CodeGenerator:
    """
    Advanced code generation engine for multiple languages and robotics
    """
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Code generation templates for robotics
        self.robotics_templates = {
            "ros2_python": self._get_ros2_python_template(),
            "ros2_cpp": self._get_ros2_cpp_template(),
            "arduino": self._get_arduino_template()
        }
    
    async def generate_code(
        self,
        description: str,
        language: str = "python",
        include_tests: bool = True,
        optimize: bool = False
    ) -> CodeResult:
        """
        Generate code from description
        
        Args:
            description: What the code should do
            language: Programming language
            include_tests: Whether to generate tests
            optimize: Whether to optimize the code
            
        Returns:
            CodeResult with generated code
        """
        # Check if robotics language
        is_robotics = language in ["ros2_python", "ros2_cpp", "arduino", "micropython"]
        
        if is_robotics:
            result = await self._generate_robotics_code(description, language)
        else:
            result = await self._generate_general_code(description, language)
        
        # Generate tests if requested
        if include_tests:
            result.tests = await self._generate_tests(result.code, language, description)
        
        # Optimize if requested  
        if optimize:
            result.code = await self._optimize_code(result.code, language)
            result.quality_score += 0.1
        
        # Analyze code quality
        result.quality_score = await self._analyze_quality(result.code, language)
        
        return result
    
    async def _generate_general_code(
        self,
        description: str,
        language: str
    ) -> CodeResult:
        """Generate general purpose code"""
        prompt = f"""Generate high-quality {language} code for the following requirement:

{description}

Requirements:
- Follow best practices and design patterns
- Include comprehensive error handling
- Add detailed comments and docstrings
- Make code maintainable and scalable
- Include type hints/annotations where applicable

Provide ONLY the code, with comments explaining key parts."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an expert {language} developer. Generate production-quality code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        code = response.choices[0].message.content
        
        # Extract code from markdown if present
        code = self._extract_code_from_markdown(code)
        
        # Generate explanation
        explanation = await self._explain_code(code, language, description)
        
        # Identify dependencies
        dependencies = await self._identify_dependencies(code, language)
        
        return CodeResult(
            language=language,
            code=code,
            explanation=explanation,
            dependencies=dependencies,
            quality_score=0.8
        )
    
    async def _generate_robotics_code(
        self,
        description: str,
        language: str
    ) -> CodeResult:
        """Generate robotics-specific code"""
        template = self.robotics_templates.get(language, "")
        
        prompt = f"""Generate {language} code for robotics application:

{description}

Template/Context:
{template}

Requirements for robotics code:
- Real-time performance considerations
- Safety checks and error handling
- Proper resource management
- Hardware interface handling
- Communication protocol implementation
- Sensor data processing

Provide complete, production-ready robotics code."""

        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        code = response.content[0].text
        code = self._extract_code_from_markdown(code)
        
        explanation = await self._explain_code(code, language, description)
        dependencies = await self._identify_dependencies(code, language)
        
        return CodeResult(
            language=language,
            code=code,
            explanation=explanation,
            dependencies=dependencies,
            quality_score=0.85
        )
    
    async def _generate_tests(
        self,
        code: str,
        language: str,
        description: str
    ) -> str:
        """Generate tests for the code"""
        test_framework = {
            "python": "pytest",
            "javascript": "jest",
            "typescript": "jest",
            "cpp": "gtest",
            "java": "junit",
            "go": "testing",
            "rust": "cargo test"
        }.get(language, "appropriate testing framework")
        
        prompt = f"""Generate comprehensive tests for this {language} code using {test_framework}:

Code:
```{language}
{code}
```

Original requirement: {description}

Generate tests that cover:
- Normal cases
- Edge cases
- Error conditions
- Integration scenarios

Provide complete test code."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an expert at writing tests in {language}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        tests = response.choices[0].message.content
        return self._extract_code_from_markdown(tests)
    
    async def _optimize_code(self, code: str, language: str) -> str:
        """Optimize code for performance and readability"""
        prompt = f"""Optimize this {language} code for:
1. Performance
2. Memory efficiency
3. Readability
4. Maintainability

Original code:
```{language}
{code}
```

Provide optimized version with same functionality."""

        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        optimized = response.content[0].text
        return self._extract_code_from_markdown(optimized)
    
    async def _analyze_quality(self, code: str, language: str) -> float:
        """Analyze code quality"""
        prompt = f"""Analyze this {language} code and rate its quality (0.0 to 1.0):

```{language}
{code}
```

Consider:
- Best practices
- Error handling
- Code organization
- Documentation
- Efficiency

Provide only a numeric score between 0.0 and 1.0."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a code quality expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        try:
            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            return max(0.0, min(1.0, score))
        except:
            return 0.7  # Default score
    
    async def _explain_code(
        self,
        code: str,
        language: str,
        description: str
    ) -> str:
        """Generate explanation for the code"""
        prompt = f"""Explain how this {language} code solves the requirement:

Requirement: {description}

Code:
```{language}
{code}
```

Provide a clear explanation of the approach, key algorithms, and how it meets the requirements."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at explaining code clearly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    async def _identify_dependencies(
        self,
        code: str,
        language: str
    ) -> List[str]:
        """Identify code dependencies"""
        dependencies = []
        
        # Simple pattern matching for common imports
        lines = code.split('\n')
        
        if language == "python":
            for line in lines:
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    dep = line.strip().split()[1].split('.')[0]
                    if dep not in ['os', 'sys', 'typing', 'dataclasses']:
                        dependencies.append(dep)
        
        elif language in ["javascript", "typescript"]:
            for line in lines:
                if 'require(' in line or 'from' in line and 'import' in line:
                    # Extract package name
                    if "'" in line:
                        dep = line.split("'")[1]
                        if not dep.startswith('.'):
                            dependencies.append(dep)
        
        return list(set(dependencies))
    
    def _extract_code_from_markdown(self, text: str) -> str:
        """Extract code from markdown code blocks"""
        if '```' in text:
            parts = text.split('```')
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Odd indices are code blocks
                    # Remove language identifier
                    lines = part.split('\n')
                    if lines:
                        return '\n'.join(lines[1:]) if lines[0].strip() in Language._value2member_map_ or not lines[0].strip()[0].isalpha() else part
        return text
    
    def _get_ros2_python_template(self) -> str:
        """Get ROS2 Python template"""
        return """
# ROS2 Python Node Template
import rclpy
from rclpy.node import Node
# Include appropriate message types
# Implement proper lifecycle management
# Handle callbacks and timers correctly
# Implement quality of service (QoS) settings
        """
    
    def _get_ros2_cpp_template(self) -> str:
        """Get ROS2 C++ template"""
        return """
// ROS2 C++ Node Template
#include "rclcpp/rclcpp.hpp"
// Include appropriate message headers
// Implement proper RAII patterns
// Handle threading correctly
// Implement QoS settings
        """
    
    def _get_arduino_template(self) -> str:
        """Get Arduino template"""
        return """
// Arduino Template
void setup() {
    // Initialize hardware
    Serial.begin(9600);
}

void loop() {
    // Main loop
    // Handle sensors and actuators
}
        """


# Global code generator instance
code_generator = CodeGenerator()
