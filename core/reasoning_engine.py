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

from core.self_learning import learning_system


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

    async def reason(self, query: str, depth: str = "deep", model: str = "auto") -> ReasoningResult:
        """
        Main reasoning method using chain-of-thought
        
        Args:
            query: The problem or question to reason about
            depth: Reasoning depth - "quick", "normal", or "deep"
            
        Returns:
            ReasoningResult with complete reasoning chain
        """
        if self.mock_llm:
            return await self._mock_reason(query, depth)

        # Optimization: Short-circuit for simple greetings or very short queries
        # This prevents unnecessary "Decomposition" of "hello" into 12 sub-problems
        simple_queries = ["hello", "hi", "hey", "greetings", "ping", "test"]
        is_simple = query.lower().strip().strip('!.?') in simple_queries or len(query.split()) < 2
        
        if is_simple and depth != "deep":
            try:
                # Direct response for simple queries
                prompt = f"User says: {query}\nProvide a friendly, direct, and concise response without complex reasoning."
                response_text = await self._query_gemini(prompt)
                
                return ReasoningResult(
                    query=query,
                    steps=[ThoughtStep(1, "Direct response for simple query", "Query was identified as simple/greeting, skipping deep reasoning chain.", 1.0)],
                    conclusion=response_text,
                    confidence=1.0,
                    execution_time=0.1
                )
            except Exception:
                # Fallback to normal flow if direct query fails
                pass

        start_time = datetime.now()
        
        # Step 0: Retrieve learned memories/suggestions
        memories = learning_system.get_improvement_suggestions(query)
        if memories:
             print(f"🧠 Retrieved {len(memories)} memories for context")

        # Step 1: Decompose the problem
        decomposition = await self._decompose_problem(query, memories)
        
        # Step 2: Plan the approach
        plan = await self._create_plan(query, decomposition, memories)
        
        # Step 3: Execute reasoning steps
        steps = await self._execute_reasoning_chain(query, plan, depth, model, memories)
        
        # Step 4: Synthesize conclusion
        conclusion = await self._synthesize_conclusion(query, steps)
        
        # Step 5: Reflect and validate
        validated_conclusion, confidence = await self._reflect_and_validate(
            query, steps, conclusion
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Store in memory
        self._store_in_memory(query, steps, validated_conclusion)
        
        return ReasoningResult(
            query=query,
            steps=steps,
            conclusion=validated_conclusion,
            confidence=confidence,
            execution_time=execution_time
        )
    
    async def _decompose_problem(self, query: str, memories: List[str] = None) -> List[str]:
        """Break down complex problem into sub-problems"""
        prompt = f"""Decompose this problem into logical sub-problems:

Problem: {query}

Provide a numbered list of sub-problems that need to be addressed to solve this.

Memories from past interactions:
{chr(10).join(memories) if memories else "None"}"""

        try:
            decomposition_text = await self._query_gemini(prompt)
        except Exception as e:
            print(f"Gemini decomposition failed: {e}, using fallback")
            # Fallback Logic (Mock or simplified)
            decomposition_text = "1. Analyze the request\n2. Formulate a response"

        # Parse decomposition
        sub_problems = [line.strip() for line in decomposition_text.split('\n') 
                       if line.strip() and any(char.isdigit() for char in line[:3])]
        
        return sub_problems
    
    async def _create_plan(self, query: str, decomposition: List[str], memories: List[str] = None) -> Dict[str, Any]:
        """Create execution plan based on problem decomposition"""
        prompt = f"""Create a step-by-step plan to solve this problem:

Problem: {query}

Sub-problems identified:
{chr(10).join(decomposition)}

Provide a detailed execution plan with specific steps.

Consider these past lessons:
{chr(10).join(memories) if memories else "None"}"""

        try:
            plan_text = await self._query_gemini(prompt)
        except Exception as e:
            print(f"Gemini planning failed: {e}")
            plan_text = "Step 1: Analyze input\nStep 2: Generate response"

        return {
            "steps": plan_text.split('\n'),
            "sub_problems": decomposition
        }
    
    async def _execute_reasoning_chain(
        self, 
        query: str, 
        plan: Dict[str, Any],
        depth: str,
        model: str = "auto",
        memories: List[str] = None
    ) -> List[ThoughtStep]:
        """Execute the reasoning chain step by step with optional model enforcement"""
        steps = []
        num_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        for i in range(num_steps):
            prompt = self._build_step_prompt(query, plan, steps, i + 1, memories)
            
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
                    # Fallback if Llama requested but not available
                    thought, reasoning, confidence = await self._reason_with_openai(prompt)
                else:
                    # Default fallback
                    thought, reasoning, confidence = await self._reason_with_openai(prompt)
            else:
                # Auto rotation logic
                # Pattern: Ollama (if enabled) -> OpenAI -> Anthropic -> Gemini
                model_index = i % 4 if self.use_ollama else i % 3
                
                if self.use_ollama and model_index == 0:
                     thought, reasoning, confidence = await self._reason_with_ollama(prompt)
                else:
                    # Default to Gemini for all other steps in auto mode
                    thought, reasoning, confidence = await self._reason_with_gemini(prompt)
            
            step = ThoughtStep(
                step_number=i + 1,
                thought=thought,
                reasoning=reasoning,
                confidence=confidence
            )
            steps.append(step)
        
        return steps
    
    def _build_step_prompt(
        self,
        query: str,
        plan: Dict[str, Any],
        previous_steps: List[ThoughtStep],
        step_number: int,
        memories: List[str] = None
    ) -> str:
        """Build prompt for current reasoning step"""
        previous_thoughts = "\n".join([
            f"Step {s.step_number}: {s.thought}" for s in previous_steps
        ])
        
        return f"""You are reasoning through this problem step by step:

Problem: {query}

Plan: {chr(10).join(plan['steps'][:3])}

Previous reasoning steps:
{previous_thoughts if previous_thoughts else "None yet - this is the first step"}

Current step {step_number}:
Provide your next logical thought and detailed reasoning for this step.
Focus on moving toward a solution.

Relevant past learnings:
{chr(10).join(memories) if memories else "None"}"""
    
    async def _reason_with_openai(self, prompt: str) -> tuple[str, str, float]:
        """Perform reasoning using OpenAI's model"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a brilliant reasoning engine. Think step by step with clear logic."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Parse thought and reasoning
            lines = content.split('\n')
            thought = lines[0] if lines else content[:100]
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            return thought, reasoning, 0.85
        except Exception as e:
            print(f"⚠️ OpenAI reasoning failed: {e}")
            # Fallback to Gemini if OpenAI fails
            if self.gemini_client:
                return await self._reason_with_gemini(prompt)
            return "Thinking...", f"Error: {str(e)}", 0.0

    async def _reason_with_anthropic(self, prompt: str) -> tuple[str, str, float]:
        """Perform reasoning using Anthropic's model"""
        try:
            if not os.getenv("ANTHROPIC_API_KEY"):
                 raise Exception("No Anthropic API Key")

            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
            # Parse thought and reasoning
            lines = content.split('\n')
            thought = lines[0] if lines else content[:100]
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            return thought, reasoning, 0.87
        except Exception as e:
            print(f"⚠️ Anthropic reasoning failed: {e}")
             # Fallback to Gemini if Anthropic fails
            if self.gemini_client:
                return await self._reason_with_gemini(prompt)
            return "Thinking...", f"Error: {str(e)}", 0.0

    async def _reason_with_ollama(self, prompt: str) -> tuple[str, str, float]:
        """Perform reasoning using Ollama's local Llama model"""
        if not self.use_ollama:
            # Fallback to Gemini if Ollama not available or disabled
            return await self._reason_with_gemini(prompt)
        
        try:
            # Use invoke for synchronous call (LangChain Ollama doesn't support async well yet)
            import asyncio
            response = await asyncio.to_thread(
                self.ollama_client.invoke,
                prompt
            )
            
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse thought and reasoning
            lines = content.split('\n')
            thought = lines[0] if lines else content[:100]
            reasoning = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            return thought, reasoning, 0.90  # High confidence for local model
        except Exception as e:
            print(f"⚠️ Ollama reasoning failed: {e}, falling back to Gemini")
            return await self._reason_with_gemini(prompt)

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

    async def _reflect_and_validate(
        self,
        query: str,
        steps: List[ThoughtStep],
        conclusion: str
    ) -> tuple[str, float]:
        """Reflect on reasoning and validate conclusion"""
        prompt = f"""Reflect on this reasoning process and validate the conclusion:

Question: {query}

Conclusion: {conclusion}

Reasoning steps: {len(steps)} steps taken

Tasks:
1. Identify any logical gaps or errors
2. Assess confidence in the conclusion (0.0 to 1.0)
3. Provide final validated conclusion

Format:
Confidence: [0.0-1.0]
Final Conclusion: [validated conclusion]"""

        try:
            content = await self._query_gemini(prompt)
        except Exception as e:
            print(f"Gemini reflection failed: {e}")
            content = "Confidence: 0.8\nFinal Conclusion: " + conclusion
        
        # Parse confidence and conclusion
        confidence = 0.8  # Default
        validated_conclusion = conclusion
        
        for line in content.split('\n'):
            if line.startswith('Confidence:'):
                try:
                    confidence = float(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith('Final Conclusion:'):
                validated_conclusion = line.split(':', 1)[1].strip()
        
        return validated_conclusion, confidence

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

        # Optimization: Short-circuit for simple greetings
        simple_queries = ["hello", "hi", "hey", "greetings", "ping", "test"]
        is_simple = query.lower().strip().strip('!.?') in simple_queries or len(query.split()) < 2
        
        if is_simple and depth != "deep":
            yield json.dumps({"type": "thought", "data": "Identified simple query. Responding directly..."}) + "\n"
            try:
                # Direct streaming response for simple queries
                prompt = f"User says: {query}\nProvide a friendly, direct, and concise response."
                
                # Stream the content directly
                # We need to use the generative model's stream feature if available, or just mock stream
                if self.gemini_client:
                     # Use synchronous stream in thread
                    def stream_gemini():
                        return self.gemini_client.models.generate_content_stream(
                            model=self.gemini_model,
                            contents=prompt
                        )
                    
                    stream = await asyncio.to_thread(stream_gemini)
                    
                    for chunk in stream:
                        if chunk.text:
                             yield json.dumps({"type": "content", "data": chunk.text}) + "\n"
                    return
            except Exception as e:
                 print(f"Direct stream failed: {e}, falling back to deep reasoning")

        # Step 1: Decompose
        yield json.dumps({"type": "thought", "data": "Analyzing request..."}) + "\n"
        
        # Retrieve memories
        memories = learning_system.get_improvement_suggestions(query)
        if memories:
             yield json.dumps({"type": "thought", "data": f"Recall: Found {len(memories)} relevant past lessons"}) + "\n"

        decomposition = await self._decompose_problem(query, memories)
        yield json.dumps({"type": "thought", "data": f"Decomposed into {len(decomposition)} sub-problems"}) + "\n"
        
        # Step 2: Plan
        plan = await self._create_plan(query, decomposition, memories)
        yield json.dumps({"type": "thought", "data": "Plan created. Executing reasoning chain..."}) + "\n"
        
        # Step 3: Execute (Streaming)
        steps = []
        num_steps = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        for i in range(num_steps):
            yield json.dumps({"type": "thought", "data": f"Step {i+1}: Reasoning..."}) + "\n"
            
            prompt = self._build_step_prompt(query, plan, steps, i + 1, memories)
            
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
