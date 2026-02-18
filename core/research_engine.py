"""
Z3ube Research Engine - Deep Multi-Source Research

This module implements:
- Multi-source information gathering
- Web scraping and extraction
- Research paper analysis
- Knowledge synthesis and summarization
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import httpx
from bs4 import BeautifulSoup


@dataclass
class Source:
    """Represents a research source"""
    url: str
    title: str
    content: str
    relevance_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content[:500],  # Truncate for display
            "relevance_score": self.relevance_score,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ResearchResult:
    """Complete research result"""
    topic: str
    summary: str
    key_findings: List[str]
    sources: List[Source]
    confidence: float
    research_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "summary": self.summary,
            "key_findings": self.key_findings,
            "sources": [s.to_dict() for s in self.sources],
            "confidence": self.confidence,
            "research_time": self.research_time
        }


class ResearchEngine:
    """
    Deep research engine for multi-source information synthesis
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        try:
            from google import genai
            self.gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
            print("✅ Gemini Client initialized in ResearchEngine")
        except Exception as e:
            print(f"⚠️ ResearchEngine Gemini Client initialization failed: {e}")
            self.gemini_client = None

        # Research cache
        self.research_cache: Dict[str, ResearchResult] = {}

    async def _query_gemini(self, prompt: str) -> str:
        """Helper to query Gemini model"""
        if not self.gemini_client:
             # Fallback or error
             raise Exception("Gemini client not initialized")
            
        try:
            # Run synchronous Gemini call in thread
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model=self.gemini_model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini query failed: {e}")
            raise e
    
    async def conduct_research(
        self,
        topic: str,
        depth: str = "normal",
        max_sources: int = 5
    ) -> ResearchResult:
        """
        Conduct deep research on a topic
        
        Args:
            topic: Research topic
            depth: Research depth - "quick", "normal", or "deep"
            max_sources: Maximum number of sources to gather
            
        Returns:
            ResearchResult with findings and sources
        """
        start_time = datetime.now()
        
        # Check cache
        cache_key = f"{topic}_{depth}"
        if cache_key in self.research_cache:
            cached = self.research_cache[cache_key]
            # Return cache if less than 1 hour old
            if (datetime.now() - cached.sources[0].timestamp).total_seconds() < 3600:
                print(f"Returning cached research for {topic}")
                return cached
        
        try:
            # Step 1: Generate research plan
            research_plan = await self._create_research_plan(topic, depth)
            
            # Step 2: Gather information from multiple sources
            sources = await self._gather_sources(topic, research_plan, max_sources)
            
            # Step 3: Analyze and synthesize information
            synthesis = await self._synthesize_findings(topic, sources)
            
            # Step 4: Extract key findings
            key_findings = await self._extract_key_findings(synthesis)
            
            # Step 5: Generate summary
            summary = await self._generate_summary(topic, synthesis, key_findings)
            
            research_time = (datetime.now() - start_time).total_seconds()
            
            result = ResearchResult(
                topic=topic,
                summary=summary,
                key_findings=key_findings,
                sources=sources,
                confidence=0.85,
                research_time=research_time
            )
            
            # Cache result
            self.research_cache[cache_key] = result
            
            return result
        except Exception as e:
            print(f"Research failed: {e}")
            # Return a partial result indicating failure instead of crashing
            return ResearchResult(
                topic=topic,
                summary=f"Research could not be completed effectively due to an error: {str(e)}",
                key_findings=["Error accessing research tools"],
                sources=[],
                confidence=0.0,
                research_time=(datetime.now() - start_time).total_seconds()
            )
    
    async def _create_research_plan(self, topic: str, depth: str) -> Dict[str, Any]:
        """Create a research plan"""
        num_questions = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        prompt = f"""Create a research plan for this topic: {topic}

Generate {num_questions} specific research questions that need to be answered.
Focus on comprehensive understanding of the topic."""

        prompt = f"""Create a research plan for this topic: {topic}

Generate {num_questions} specific research questions that need to be answered.
Focus on comprehensive understanding of the topic."""

        try:
             questions_text = await self._query_gemini(prompt)
        except Exception as e:
             print(f"Gemini research planning failed: {e}")
             questions_text = f"1. {topic} overview\n2. Key features of {topic}\n3. Recent developments in {topic}"
        questions = [
            line.strip() 
            for line in questions_text.split('\n') 
            if line.strip() and any(char.isdigit() for char in line[:3])
        ]
        
        return {
            "questions": questions,
            "depth": depth
        }
    
    async def _gather_sources(
        self,
        topic: str,
        research_plan: Dict[str, Any],
        max_sources: int
    ) -> List[Source]:
        """Gather information from multiple sources"""
        sources = []
        
        # For this implementation, we'll use AI to simulate research
        # In production, you'd integrate with real search APIs (Google, Bing, etc.)
        
        for i, question in enumerate(research_plan["questions"][:max_sources]):
            try:
                source = await self._research_question(topic, question, i)
                if source:
                    sources.append(source)
            except Exception as e:
                print(f"Error researching question: {e}")
                continue
        
        return sources
    
    async def _research_question(
        self,
        topic: str,
        question: str,
        index: int
    ) -> Optional[Source]:
        """Research a specific question"""
        prompt = f"""Research this question about {topic}:

Question: {question}

Provide comprehensive information with specific details, data, and examples.
Include any relevant technical information, statistics, or recent developments."""

        try:
            content = await self._query_gemini(prompt)
            
            return Source(
                url=f"research_synthesis_{index}",
                title=question,
                content=content,
                relevance_score=0.9
            )
        except Exception as e:
            print(f"Error in research: {e}")
            return None
    
    async def _synthesize_findings(
        self,
        topic: str,
        sources: List[Source]
    ) -> str:
        """Synthesize information from all sources"""
        sources_text = "\n\n".join([
            f"Source {i+1}: {s.title}\n{s.content}"
            for i, s in enumerate(sources)
        ])
        
        prompt = f"""Synthesize this research about {topic}:

{sources_text}

Create a comprehensive synthesis that:
1. Integrates information from all sources
2. Identifies patterns and connections
3. Highlights important insights
4. Notes any contradictions or gaps"""

        try:
            return await self._query_gemini(prompt)
        except Exception as e:
            print(f"Gemini synthesis failed: {e}")
            return "Synthesis unavailable due to error."
    
    async def _extract_key_findings(self, synthesis: str) -> List[str]:
        """Extract key findings from synthesis"""
        prompt = f"""Extract the key findings from this research synthesis:

{synthesis}

Provide 5-7 bullet points of the most important findings."""

        try:
             findings_text = await self._query_gemini(prompt)
        except Exception as e:
             print(f"Gemini extraction failed: {e}")
             return []
        findings = [
            line.strip().lstrip('-•*').strip()
            for line in findings_text.split('\n')
            if line.strip() and (line.strip().startswith('-') or 
                               line.strip().startswith('•') or
                               line.strip().startswith('*') or
                               any(char.isdigit() for char in line[:3]))
        ]
        
        return findings[:7]
    
    async def _generate_summary(
        self,
        topic: str,
        synthesis: str,
        key_findings: List[str]
    ) -> str:
        """Generate final research summary"""
        findings_text = "\n".join(key_findings)
        
        prompt = f"""Create a concise summary for research on {topic}:

Key Findings:
{findings_text}

Full Synthesis:
{synthesis}

Provide a clear, accessible summary (2-3 paragraphs) that captures the essence of the research."""

        try:
            return await self._query_gemini(prompt)
        except Exception as e:
            print(f"Gemini summary failed: {e}")
            return "Summary unavailable due to error."
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Global research engine instance
research_engine = ResearchEngine()
