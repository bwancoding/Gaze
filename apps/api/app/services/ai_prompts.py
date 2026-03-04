"""
WRHITW AI Prompt Templates
多视角新闻摘要生成系统
"""

from typing import List, Dict, Any
from jinja2 import Template
import json


class PromptTemplate:
    """Prompt 模板基类"""
    
    def __init__(self, template_str: str):
        self.template = Template(template_str)
    
    def render(self, **kwargs) -> str:
        """渲染 Prompt"""
        return self.template.render(**kwargs)


class MultiPerspectiveSummaryPrompt(PromptTemplate):
    """多视角摘要生成 Prompt"""
    
    TEMPLATE = """
# Role
你是一位专业的新闻分析师，擅长从多篇报道中提取不同视角的信息。

# Task
根据以下媒体报道，生成三个不同视角的摘要（左倾、中立、右倾）。

# Input Data
## 左倾媒体报道
{% for article in left_articles %}
### {{ article.source_name }}
标题：{{ article.title }}
内容：{{ article.content[:2000] }}
{% endfor %}

## 中立媒体报道
{% for article in center_articles %}
### {{ article.source_name }}
标题：{{ article.title }}
内容：{{ article.content[:2000] }}
{% endfor %}

## 右倾媒体报道
{% for article in right_articles %}
### {{ article.source_name }}
标题：{{ article.title }}
内容：{{ article.content[:2000] }}
{% endfor %}

# Requirements
1. **每个视角 150-250 字**
2. **客观陈述，不添加个人评价**
3. **突出不同视角的关注点差异**
4. **每个视角末尾标注信息来源**
5. **使用中性语言，避免情绪化词汇**

# Output Format
请严格按照以下 JSON 格式输出：

```json
{
  "left_perspective": {
    "summary": "左倾视角摘要内容",
    "sources": ["媒体 A", "媒体 B"],
    "key_focus": ["关注点 1", "关注点 2"]
  },
  "center_perspective": {
    "summary": "中立视角摘要内容",
    "sources": ["媒体 C", "媒体 D"],
    "key_focus": ["关注点 1", "关注点 2"]
  },
  "right_perspective": {
    "summary": "右倾视角摘要内容",
    "sources": ["媒体 E", "媒体 F"],
    "key_focus": ["关注点 1", "关注点 2"]
  },
  "event_title": "中性的事件标题",
  "confidence_score": 0.95
}
```

# Notes
- 如果某个视角的报道不足，可以留空，但需说明原因
- confidence_score 表示你对摘要准确性的信心（0-1）
"""
    
    def __init__(self):
        super().__init__(self.TEMPLATE)
    
    def render(self, left_articles: List[Dict], center_articles: List[Dict], right_articles: List[Dict]) -> str:
        return super().render(
            left_articles=left_articles,
            center_articles=center_articles,
            right_articles=right_articles
        )


class BiasAnalysisPrompt(PromptTemplate):
    """偏见分析 Prompt"""
    
    TEMPLATE = """
# Role
你是一位媒体偏见分析专家，擅长识别新闻报道中的立场倾向。

# Task
分析以下文章的偏见倾向，给出左/中/右的判断和依据。

# Input Data
## 文章信息
标题：{{ title }}
来源：{{ source_name }}
发布时间：{{ published_at }}

## 文章内容
{{ content[:3000] }}

# Analysis Dimensions
请从以下维度分析：

1. **用词倾向**
   - 是否使用情绪化词汇？
   - 对同一事件的正/负面描述？

2. **信息选择**
   - 强调了哪些事实？
   - 忽略了哪些事实？

3. **消息来源**
   - 引用了哪些人的观点？
   - 是否有单一倾向？

4. **框架设定**
   - 如何定义问题？
   - 暗示了什么解决方案？

# Output Format
请严格按照以下 JSON 格式输出：

```json
{
  "bias_label": "left|center|right",
  "bias_score": -0.5,
  "confidence": 0.85,
  "analysis": {
    "word_choice": "用词分析",
    "information_selection": "信息选择分析",
    "sources_used": "消息来源分析",
    "framing": "框架设定分析"
  },
  "evidence": [
    "具体证据 1（引用原文）",
    "具体证据 2（引用原文）"
  ]
}
```

# Bias Scale
- -1.0 ~ -0.5: 明显左倾
- -0.5 ~ -0.1: 轻微左倾
- -0.1 ~ 0.1: 中立
- 0.1 ~ 0.5: 轻微右倾
- 0.5 ~ 1.0: 明显右倾
"""
    
    def __init__(self):
        super().__init__(self.TEMPLATE)
    
    def render(self, title: str, source_name: str, published_at: str, content: str) -> str:
        return super().render(
            title=title,
            source_name=source_name,
            published_at=published_at,
            content=content
        )


class AISummaryGenerator:
    """AI 摘要生成器"""
    
    def __init__(self, client):
        self.client = client
        self.summary_prompt = MultiPerspectiveSummaryPrompt()
        self.bias_prompt = BiasAnalysisPrompt()
    
    async def generate_summary(self, articles: List[Dict]) -> Dict[str, Any]:
        """
        生成多视角摘要
        
        Args:
            articles: 文章列表，每篇包含 source_name, title, content, bias_label
        
        Returns:
            多视角摘要结果
        """
        # 按立场分组
        left_articles = [a for a in articles if a.get('bias_label') == 'left']
        center_articles = [a for a in articles if a.get('bias_label') == 'center']
        right_articles = [a for a in articles if a.get('bias_label') == 'right']
        
        # 渲染 Prompt
        prompt = self.summary_prompt.render(
            left_articles=left_articles,
            center_articles=center_articles,
            right_articles=right_articles
        )
        
        # 调用 AI
        response = await self.client.chat.completions.create(
            model="qwen3.5-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # 解析结果
        result = json.loads(response.choices[0].message.content)
        
        return result
    
    async def analyze_bias(self, article: Dict) -> Dict[str, Any]:
        """
        分析文章偏见
        
        Args:
            article: 文章信息
        
        Returns:
            偏见分析结果
        """
        prompt = self.bias_prompt.render(
            title=article['title'],
            source_name=article['source_name'],
            published_at=article.get('published_at', ''),
            content=article.get('content', '')
        )
        
        response = await self.client.chat.completions.create(
            model="qwen3.5-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)


# 使用示例
if __name__ == "__main__":
    # 示例用法
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(
        base_url="https://coding.dashscope.aliyuncs.com/v1",
        api_key="your-api-key"
    )
    
    generator = AISummaryGenerator(client)
    
    # 示例文章
    articles = [
        {
            "source_name": "The Guardian",
            "title": "Workers celebrate wage increase",
            "content": "...",
            "bias_label": "left"
        },
        {
            "source_name": "Reuters",
            "title": "Government announces wage policy change",
            "content": "...",
            "bias_label": "center"
        },
        {
            "source_name": "Fox News",
            "title": "Businesses face higher labor costs",
            "content": "...",
            "bias_label": "right"
        }
    ]
    
    # 生成摘要
    # result = await generator.generate_summary(articles)
