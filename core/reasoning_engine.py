"""
Z3ube Reasoning Engine - Advanced Chain-of-Thought Processing

This module implements sophisticated multi-step reasoning with:
- Chain-of-Thought decomposition
- Plan-Execute-Reflect loops
- Memory retention and context awareness
- Adaptive reasoning strategies
"""

import os
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from langchain_ollama import ChatOllama


@dataclass
class ThoughtStep:
    """Represents a single step in the reasoning chain"""
    step_number: int
    thought: str
    reasoning: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "thought": self.thought,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ReasoningResult:
    """Complete reasoning chain result"""
    query: str
    steps: List[ThoughtStep]
    conclusion: str
    confidence: float
    execution_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "steps": [step.to_dict() for step in self.steps],
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "execution_time": self.execution_time
        }


class ReasoningEngine:
    """
    Advanced reasoning engine using chain-of-thought and plan-execute-reflect patterns
    """
    
    def __init__(self):
        # Initialize AI clients
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        
        # Initialize Ollama (local LLM)
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        
        # Configure Gemini
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        
        # Configure OpenAI
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        # Configure Mock LLM for testing
        self.mock_llm = os.getenv("MOCK_LLM", "false").lower() == "true"
        
        if self.use_ollama:
            try:
                self.ollama_client = ChatOllama(
                    model=self.ollama_model,
                    base_url="http://localhost:11434",
                    temperature=0.7
                )
                print(f"✅ Ollama initialized with model: {self.ollama_model}")
            except Exception as e:
                print(f"⚠️ Ollama initialization failed: {e}")
                self.use_ollama = False
        
        # Memory storage for context
        self.short_term_memory: List[Dict[str, Any]] = []
        self.long_term_memory: List[Dict[str, Any]] = []
        
        # Initialize Gemini Client
        try:
            from google import genai
            self.gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            print("✅ Gemini Client initialized")
        except Exception as e:
            print(f"⚠️ Gemini Client initialization failed: {e}")
            self.gemini_client = None

    async def _query_gemini(self, prompt: str) -> str:
        """Helper to query Gemini model"""
        if not self.gemini_client:
            raise Exception("Gemini client not initialized")
            
        # Run synchronous Gemini call in thread
        try:
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model=self.gemini_model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini query failed: {e}")
            raise e

    async def _reason_with_gemini(self, prompt: str) -> tuple[str, str, float]:
        """Perform reasoning using Google's Gemini model via new SDK"""
        try:
            # Check if client initialized
            if not self.gemini_client:
                 # Fallback to OpenAI if Gemini fails or not init
                print("⚠️ Gemini client not ready, falling back to OpenAI")
                return await self._reason_with_openai(prompt)

            from google import genai
            from google.genai import types
            
            # Simple prompt wrapper for Gemini
            gemini_prompt = f"System: You are a brilliant reasoning engine. Think step by step.\n\nUser: {prompt}"
            
            # Run synchronous Gemini call in thread to avoid blocking loop
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model=self.gemini_model,
                contents=gemini_prompt
            )
            
            content = response.text
            
            # Parse thought and reasoning
            lines = content.split('\n')
            thought = lines[0] if lines else content[:100]
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            return thought, reasoning, 0.88
            
        except Exception as e:
            print(f"⚠️ Gemini reasoning failed: {e}")
            return "Thinking...", f"Error: {str(e)}", 0.0

    async def _synthesize_conclusion(
        self,
        query: str,
        steps: List[ThoughtStep]
    ) -> str:
        """Synthesize final conclusion from reasoning steps"""
        steps_summary = "\n".join([
            f"Step {s.step_number}: {s.thought}" for s in steps
        ])
        
        prompt = f"""Based on this step-by-step reasoning, provide a clear conclusion:

Original question: {query}

Reasoning chain:
{steps_summary}

Synthesize these steps into a comprehensive answer."""

        try:
            return await self._query_gemini(prompt)
        except Exception as e:
            print(f"Gemini synthesis failed: {e}")
            return "Unable to synthesize conclusion due to error."

    # ... (skipping _reflect_and_validate as it uses _query_gemini which is now async)

    async def reason_stream(self, query: str, depth: str = "deep", model: str = "auto") -> AsyncGenerator[str, None]:
        """
        Stream reasoning process and final conclusion
        
        Args:
            query: The problem or question
            depth: Reasoning depth
            
        Yields:
            JSON string chunks containing 'type' (thought/content) and 'data'
        """
        if self.mock_llm:
            async for chunk in self._mock_reason_stream(query, depth):
                yield chunk
            return

        # Step 1: Decompose
        yield json.dumps({"type": "thought", "data": "Analyzing request..."}) + "\n"
        decomposition = await self._decompose_problem(query)
        yield json.dumps({"type": "thought", "data": f"Decomposed into {len(decomposition)} sub-problems"}) + "\n"
        
        # Step 2: Plan
        plan = await self._create_plan(query, decomposition)
        yield json.dumps({"type": "thought", "data": "Plan created. Executing reasoning chain..."}) + "\n"
        
        # Step 3: Execute (Streaming)
        steps = []
        num_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        for i in range(num_steps):
            yield json.dumps({"type": "thought", "data": f"Step {i+1}: Reasoning..."}) + "\n"
            
            prompt = self._build_step_prompt(query, plan, steps, i + 1)
            
            # Determine which model to use
            if model != "auto":
                target_model = model.lower()
                if target_model == "openai":
                    thought, reasoning, confidence = await self._reason_with_openai(prompt)
                elif target_model == "anthropic":
                    thought, reasoning, confidence = await self._reason_with_anthropic(prompt)
                elif target_model == "gemini":
                    thought, reasoning, confidence = await self._reason_with_gemini(prompt)
                elif target_model == "llama" and self.use_ollama:
                    thought, reasoning, confidence = await self._reason_with_ollama(prompt)
                elif target_model == "llama" and not self.use_ollama:
                    # Fallback
                    thought, reasoning, confidence = await self._reason_with_openai(prompt)
                else:
                    thought, reasoning, confidence = await self._reason_with_openai(prompt)
            else:
                 # Use Gemini for auto mode
                 thought, reasoning, confidence = await self._reason_with_gemini(prompt)
            
            step = ThoughtStep(i + 1, thought, reasoning, confidence)
            steps.append(step)
            
            yield json.dumps({
                "type": "step", 
                "data": {
                    "step": i+1, 
                    "thought": thought,
                    "reasoning": reasoning[:100] + "..." 
                }
            }) + "\n"
            
        # Step 4: Synthesize (Streamed)
        yield json.dumps({"type": "thought", "data": "Synthesizing final answer..."}) + "\n"
        
        steps_summary = "\n".join([f"Step {s.step_number}: {s.thought}" for s in steps])
        prompt = f"""Based on this step-by-step reasoning, provide a clear conclusion:
Original question: {query}
Reasoning chain:
{steps_summary}
Synthesize these steps into a comprehensive answer."""

        # Use non-streaming call to avoid blocking loop with standard iterator
        try:
            content = await self._query_gemini(prompt)
            # Simulate streaming by splitting by lines or words if needed, or just send whole blob
            # Sending as one chunk for now to ensure stability
            yield json.dumps({"type": "content", "data": content}) + "\n"
            
        except Exception as e:
            print(f"Gemini streaming failed: {e}")
            yield json.dumps({"type": "error", "data": f"Streaming failed: {str(e)}"}) + "\n"

    async def _mock_reason(self, query: str, depth: str) -> ReasoningResult:
        """Mock reasoning for testing"""
        start_time = datetime.now()
        await asyncio.sleep(1)  # Simulate latency
        
        steps = []
        num_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        for i in range(num_steps):
            steps.append(ThoughtStep(
                step_number=i+1,
                thought=f"Mock thought {i+1} for {depth} depth",
                reasoning="Mock reasoning details...",
                confidence=0.9
            ))
            
        conclusion = f"Mock conclusion for '{query}' at {depth} depth.\\n\\nHere is some code:\\n```python\\ndef hello_world():\\n    print('Hello Z3ube')\\n    return True\\n```"
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ReasoningResult(
            query=query,
            steps=steps,
            conclusion=conclusion,
            confidence=0.95,
            execution_time=execution_time
        )

    async def _mock_reason_stream(self, query: str, depth: str) -> AsyncGenerator[str, None]:
        """Mock streaming reasoning for testing"""
        yield json.dumps({"type": "thought", "data": "Mocking analysis..."}) + "\n"
        await asyncio.sleep(0.5)
        
        num_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        for i in range(num_steps):
            yield json.dumps({"type": "thought", "data": f"Step {i+1}: Mock reasoning..."}) + "\n"
            await asyncio.sleep(0.5)
            
            yield json.dumps({
                "type": "step", 
                "data": {
                    "step": i+1, 
                    "thought": f"Mock thought {i+1}",
                    "reasoning": "Mock reasoning details..." 
                }
            }) + "\n"
            
        yield json.dumps({"type": "thought", "data": "Synthesizing answer..."}) + "\n"
        await asyncio.sleep(0.5)
        
        conclusion = f"Mock conclusion for '{query}'."
        for word in conclusion.split():
            yield json.dumps({"type": "content", "data": word + " "}) + "\n"
            await asyncio.sleep(0.1)

# Global reasoning engine instance
reasoning_engine = ReasoningEngine()
