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

    TEMPLATE = """You are a senior news analyst writing for an informed general audience. Produce three distinct perspective summaries from the source articles below.

## Writing style — CRITICAL
- Write like a sharp newspaper columnist, not like a textbook or AI chatbot
- Use active voice, concrete details, and specific examples from the sources
- NEVER use: "It's important to note", "Furthermore", "Additionally", "This highlights", "It remains to be seen"
- Vary sentence length. Short sentences for impact. Longer ones when explaining complex dynamics
- State things directly — don't hedge every sentence with qualifiers
- Each perspective should read like it was written by a different journalist with a genuine worldview, not like three versions of the same careful AI output

## Perspective Definitions

**Progressive** — Focuses on human rights, equity, environmental impact, systemic causes, effects on vulnerable populations, multilateral solutions.

**Centrist/Factual** — Focuses on verified facts, institutional responses, policy mechanics, economic data, competing claims presented fairly.

**Conservative** — Focuses on sovereignty, security, rule of law, market impact, fiscal responsibility, individual liberty vs. government overreach.

## Source Articles

{% for article in articles %}
### [{{ article.source_name }}] {{ article.title }}
Bias label: {{ article.bias_label or 'unknown' }}
{{ article.content[:2000] }}

{% endfor %}

## Rules
1. Each perspective: 150-250 words in English
2. Each MUST cover different aspects — no repeating the same points
3. List 2-3 key arguments per perspective with source citations
4. Flag disputed or unverified claims

## Output — valid JSON only:

```json
{
  "left_perspective": {
    "summary": "text",
    "key_arguments": ["...", "..."],
    "sources_cited": ["Source A"],
    "focus_dimensions": ["human rights"]
  },
  "center_perspective": {
    "summary": "text",
    "key_arguments": ["...", "..."],
    "sources_cited": ["Source B"],
    "focus_dimensions": ["policy mechanics"]
  },
  "right_perspective": {
    "summary": "text",
    "key_arguments": ["...", "..."],
    "sources_cited": ["Source C"],
    "focus_dimensions": ["national security"]
  },
  "event_title": "Neutral factual title",
  "disputed_claims": ["claim — disputed by Source X"],
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

    TEMPLATE = """You are a senior geopolitical analyst writing a deep-dive briefing on a news event. Write for an informed audience who reads Foreign Affairs and The Economist — sharp, concrete, no filler.

## Writing style — CRITICAL
- Write like an experienced analyst dictating a briefing, not like an AI generating content
- Be direct and specific. Use real names, numbers, dates, and concrete details from the sources
- NEVER use: "It's important to note", "Furthermore", "Additionally", "This highlights the need for", "It remains to be seen", "This raises important questions"
- Avoid vague hedging. If something is uncertain, say why specifically, don't just add "potentially" to everything
- Vary sentence rhythm. Mix short declarative statements with longer explanatory ones
- Each stakeholder perspective should sound like that group actually talking — a defense contractor doesn't talk like an NGO worker

## Source Articles

{% for article in articles %}
### [{{ article.source_name }}] {{ article.title }}
{{ article.content[:2000] }}

{% endfor %}

## Analysis structure

1. **Background** (150-300 words): Context, history, why it matters. Be specific, not generic.

2. **Cause Chain** (3-5 causes): What led here. Each with a label, 1-2 sentence description, and source citations.

3. **Impact Analysis** (3-5 dimensions): Economic, social, environmental, political, etc. Who gets hurt, who benefits. Be concrete.

4. **Stakeholders** (3-7 groups): SPECIFIC groups (e.g. "Iranian civilians", "US defense contractors", "European energy consumers"), NOT generic labels. Each stakeholder gets:
   - 100-200 word perspective written AS IF from their viewpoint — what they care about, fear, want
   - 2-3 key arguments they'd make
   - Source citations

5. **Timeline** (3-8 events): Key moments with dates, short titles, 1-2 sentence descriptions.

6. **Disputed Claims**: Where sources disagree. What's claimed, who disputes it, what evidence exists.

## Output — valid JSON only:

```json
{
  "event_title": "Neutral factual title",
  "background": "Background text",
  "cause_chain": [
    {"cause": "label", "description": "explanation", "sources": ["Source A"]}
  ],
  "impact_analysis": [
    {"dimension": "Economic", "impact": "description", "affected_groups": ["Group A"]}
  ],
  "stakeholders": [
    {
      "stakeholder_name": "Specific Group Name",
      "perspective_text": "Their perspective...",
      "key_arguments": ["arg 1", "arg 2"],
      "sources_cited": ["Source A"]
    }
  ],
  "timeline": [
    {"timestamp": "2026-03-15", "title": "Label", "description": "What happened"}
  ],
  "disputed_claims": [
    {"claim": "The claim", "disputed_by": "Source X", "evidence": "Evidence"}
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

    def __init__(self, client, model: str = "deepseek-ai/DeepSeek-V3"):
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
                {"role": "system", "content": "You are a veteran news analyst. Write sharp, direct prose — no AI cliches or filler phrases. Respond with valid JSON only."},
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
                {"role": "system", "content": "You are a veteran geopolitical analyst writing a briefing. Be direct, specific, and concrete — no AI filler phrases. Respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)
