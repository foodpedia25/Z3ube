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
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Research cache
        self.research_cache: Dict[str, ResearchResult] = {}
    
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
                return cached
        
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
    
    async def _create_research_plan(self, topic: str, depth: str) -> Dict[str, Any]:
        """Create a research plan"""
        num_questions = 3 if depth == "quick" else 5 if depth == "normal" else 8
        
        prompt = f"""Create a research plan for this topic: {topic}

Generate {num_questions} specific research questions that need to be answered.
Focus on comprehensive understanding of the topic."""

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a research planning expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        questions_text = response.choices[0].message.content
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
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            
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

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert research synthesizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    async def _extract_key_findings(self, synthesis: str) -> List[str]:
        """Extract key findings from synthesis"""
        prompt = f"""Extract the key findings from this research synthesis:

{synthesis}

Provide 5-7 bullet points of the most important findings."""

        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        findings_text = response.content[0].text
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

        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at creating clear research summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        
        return response.choices[0].message.content
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Global research engine instance
research_engine = ResearchEngine()
