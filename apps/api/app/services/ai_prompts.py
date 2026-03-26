"""
Gaze AI Prompt Templates
Multi-perspective news summary generation system
"""

from typing import List, Dict, Any
from jinja2 import Template
import json


class PromptTemplate:
    """Base prompt template"""

    def __init__(self, template_str: str):
        self.template = Template(template_str)

    def render(self, **kwargs) -> str:
        return self.template.render(**kwargs)


class MultiPerspectiveSummaryPrompt(PromptTemplate):
    """Multi-perspective summary prompt with clear dimension-based differentiation"""

    TEMPLATE = """You are a senior news analyst for Gaze, a multi-perspective news platform. Your job is to produce three distinct perspective summaries from the source articles below.

## Perspective Definitions

Each perspective focuses on DIFFERENT DIMENSIONS of the same event:

**Progressive perspective** — Prioritizes:
- Human rights, social equity, and environmental impact
- Effects on marginalized or vulnerable populations
- Systemic causes and structural reform
- International cooperation and multilateral solutions

**Centrist/Factual perspective** — Prioritizes:
- Verified facts, timeline, and key actors
- Institutional responses and policy mechanics
- Economic data and measurable outcomes
- Balanced presentation of competing claims

**Conservative perspective** — Prioritizes:
- National sovereignty, security, and rule of law
- Economic freedom, market impact, and fiscal responsibility
- Traditional institutions and social stability
- Individual liberty vs. government overreach

## Source Articles

{% for article in articles %}
### [{{ article.source_name }}] {{ article.title }}
Bias label: {{ article.bias_label or 'unknown' }}
{{ article.content[:2000] }}

{% endfor %}

## Instructions

1. Write each perspective as 150-250 words in English
2. Each perspective MUST highlight different aspects — do not repeat the same points across perspectives
3. Use neutral, professional language within each perspective (describe the viewpoint, don't advocate)
4. For each perspective, list 2-3 key arguments and cite which source(s) support them
5. Flag any claims that are disputed or unverified across sources
6. If a perspective lacks source coverage, note this explicitly

## Output Format

Return ONLY valid JSON:

```json
{
  "left_perspective": {
    "summary": "Progressive perspective summary text",
    "key_arguments": ["argument 1", "argument 2"],
    "sources_cited": ["Source A", "Source B"],
    "focus_dimensions": ["human rights", "environmental impact"]
  },
  "center_perspective": {
    "summary": "Centrist/factual perspective summary text",
    "key_arguments": ["argument 1", "argument 2"],
    "sources_cited": ["Source C", "Source D"],
    "focus_dimensions": ["policy mechanics", "economic data"]
  },
  "right_perspective": {
    "summary": "Conservative perspective summary text",
    "key_arguments": ["argument 1", "argument 2"],
    "sources_cited": ["Source E", "Source F"],
    "focus_dimensions": ["national security", "fiscal impact"]
  },
  "event_title": "Neutral, factual event title",
  "disputed_claims": ["claim 1 — disputed by Source X"],
  "confidence_score": 0.85
}
```"""

    def __init__(self):
        super().__init__(self.TEMPLATE)

    def render(self, articles: List[Dict]) -> str:
        return super().render(articles=articles)


class BiasAnalysisPrompt(PromptTemplate):
    """Media bias analysis prompt"""

    TEMPLATE = """You are a media bias analyst. Analyze the following article for political lean and journalistic bias.

## Article
**Title:** {{ title }}
**Source:** {{ source_name }}
**Published:** {{ published_at }}

{{ content[:3000] }}

## Analysis Dimensions

1. **Language tone** — Emotional vs. neutral word choices? Loaded terms?
2. **Information selection** — What facts are emphasized? What is omitted?
3. **Source attribution** — Who is quoted? Is there ideological diversity in quotes?
4. **Framing** — How is the problem defined? What solutions are implied?

## Output Format

Return ONLY valid JSON:

```json
{
  "bias_label": "left|center-left|center|center-right|right",
  "bias_score": -0.5,
  "confidence": 0.85,
  "analysis": {
    "language_tone": "analysis of word choices and emotional language",
    "information_selection": "what facts are highlighted vs omitted",
    "source_attribution": "who is quoted and ideological diversity",
    "framing": "how the problem and solutions are framed"
  },
  "evidence": [
    "specific quote or pattern from the article"
  ]
}
```

Bias scale: -1.0 (strong left) to +1.0 (strong right), 0.0 = center."""

    def __init__(self):
        super().__init__(self.TEMPLATE)

    def render(self, title: str, source_name: str, published_at: str, content: str) -> str:
        return super().render(
            title=title,
            source_name=source_name,
            published_at=published_at,
            content=content,
        )


class StakeholderAnalysisPrompt(PromptTemplate):
    """Stakeholder-based deep analysis prompt — replaces left/center/right with dynamic stakeholders"""

    TEMPLATE = """You are a senior geopolitical and socio-economic analyst for Gaze, a multi-stakeholder news platform. Your job is to produce a comprehensive deep analysis of an event from MULTIPLE stakeholder perspectives.

## Source Articles

{% for article in articles %}
### [{{ article.source_name }}] {{ article.title }}
{{ article.content[:2000] }}

{% endfor %}

## Instructions

Analyze this event comprehensively:

1. **Background**: Write 150-300 words explaining the event context, historical background, and why it matters.

2. **Cause Chain**: Identify 3-5 causal factors that led to this event. For each, provide:
   - A short cause label
   - Description (1-2 sentences)
   - Which sources mention this cause

3. **Impact Analysis**: Identify 3-5 impact dimensions (economic, social, environmental, political, etc.). For each:
   - Dimension name
   - Impact description (1-2 sentences)
   - Which groups are most affected

4. **Stakeholder Identification**: Identify 3-7 distinct stakeholder groups who are directly affected by or have a stake in this event. These should be SPECIFIC groups (e.g., "Iranian civilians", "US defense contractors", "European energy consumers"), NOT generic political labels. For each stakeholder:
   - stakeholder_name: A clear, specific name
   - perspective_text: 100-200 words describing how this group views the event, what they care about, what they fear or hope for
   - key_arguments: 2-3 key points this group would emphasize
   - sources_cited: Which source articles support this perspective

5. **Timeline**: Construct a timeline of 3-8 key moments related to this event, each with:
   - timestamp (approximate date/time if available, or relative like "Day 1")
   - title (short label)
   - description (1-2 sentences)

6. **Disputed Claims**: Identify claims where sources disagree, each with:
   - The claim itself
   - Who disputes it
   - Available evidence

## Output Format

Return ONLY valid JSON:

```json
{
  "event_title": "Neutral, factual event title",
  "background": "Comprehensive background text",
  "cause_chain": [
    {"cause": "label", "description": "explanation", "sources": ["Source A"]}
  ],
  "impact_analysis": [
    {"dimension": "Economic", "impact": "description", "affected_groups": ["Group A", "Group B"]}
  ],
  "stakeholders": [
    {
      "stakeholder_name": "Specific Group Name",
      "perspective_text": "Their perspective on this event...",
      "key_arguments": ["argument 1", "argument 2"],
      "sources_cited": ["Source A"]
    }
  ],
  "timeline": [
    {"timestamp": "2026-03-15", "title": "Event label", "description": "What happened"}
  ],
  "disputed_claims": [
    {"claim": "The claim", "disputed_by": "Source X", "evidence": "Available evidence"}
  ],
  "confidence_score": 0.85
}
```"""

    def __init__(self):
        super().__init__(self.TEMPLATE)

    def render(self, articles: List[Dict]) -> str:
        return super().render(articles=articles)


class AISummaryGenerator:
    """AI summary generator with caching support"""

    def __init__(self, client, model: str = "qwen3.5-plus"):
        self.client = client
        self.model = model
        self.summary_prompt = MultiPerspectiveSummaryPrompt()
        self.bias_prompt = BiasAnalysisPrompt()
        self.stakeholder_prompt = StakeholderAnalysisPrompt()

    async def generate_summary(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        Generate multi-perspective summary from articles.

        Args:
            articles: List of dicts with source_name, title, content, bias_label

        Returns:
            Parsed JSON with left/center/right perspectives
        """
        prompt = self.summary_prompt.render(articles=articles)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional news analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result

    async def analyze_bias(self, article: Dict) -> Dict[str, Any]:
        """
        Analyze article bias.

        Args:
            article: Dict with title, source_name, published_at, content

        Returns:
            Parsed JSON with bias analysis
        """
        prompt = self.bias_prompt.render(
            title=article["title"],
            source_name=article["source_name"],
            published_at=article.get("published_at", ""),
            content=article.get("content", ""),
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a media bias analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    async def generate_stakeholder_analysis(self, articles: List[Dict]) -> Dict[str, Any]:
        """Generate stakeholder-based deep analysis from articles."""
        prompt = self.stakeholder_prompt.render(articles=articles)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional geopolitical analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)
