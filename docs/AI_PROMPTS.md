# WRHITW AI 提示词模板系统

🤖 **版本**: v1.0  
**创建时间**: 2026-03-04  
**适用模型**: 百炼 (qwen3.5-plus, qwen3-coder-plus)

---

## 📋 总览

WRHITW 使用 AI 完成以下核心任务：

| 任务 | Prompt 模板 | 用途 |
|------|-----------|------|
| **多视角摘要** | `multi_perspective_summary` | 生成左/中/右三个视角摘要 |
| **偏见分析** | `bias_analysis` | 分析文章的立场倾向 |
| **情感分析** | `sentiment_analysis` | 分析文章的情感色彩 |
| **事件聚类** | `event_clustering` | 判断多篇报道是否属于同一事件 |
| **标题生成** | `headline_generation` | 生成中性事件标题 |
| **质量评估** | `quality_assessment` | 评估 AI 摘要的质量 |

---

## 📝 核心 Prompt 模板

### 1. 多视角摘要生成 (Multi-Perspective Summary)

**用途**: 根据多个媒体的报道，生成左/中/右三个视角的摘要

**模板 ID**: `multi_perspective_summary_v1`

```
# Role
你是一位专业的新闻分析师，擅长从多篇报道中提取不同视角的信息。

# Task
根据以下媒体报道，生成三个不同视角的摘要（左倾、中立、右倾）。

# Input Data
## 左倾媒体报道
{% for article in left_articles %}
### {{ article.source_name }}
标题：{{ article.title }}
内容：{{ article.content }}
{% endfor %}

## 中立媒体报道
{% for article in center_articles %}
### {{ article.source_name }}
标题：{{ article.title }}
内容：{{ article.content }}
{% endfor %}

## 右倾媒体报道
{% for article in right_articles %}
### {{ article.source_name }}
标题：{{ article.title }}
内容：{{ article.content }}
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
```

---

### 2. 偏见分析 (Bias Analysis)

**用途**: 分析单篇文章的政治立场倾向

**模板 ID**: `bias_analysis_v1`

```
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
{{ content }}

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
```

---

### 3. 情感分析 (Sentiment Analysis)

**用途**: 分析文章对特定事件/人物的情感倾向

**模板 ID**: `sentiment_analysis_v1`

```
# Role
你是一位情感分析专家，擅长识别文本中的情感色彩。

# Task
分析以下文章对核心事件的情感倾向。

# Input Data
## 文章信息
标题：{{ title }}
来源：{{ source_name }}

## 文章内容
{{ content }}

## 核心事件/人物
{{ target_event }}

# Output Format
请严格按照以下 JSON 格式输出：

```json
{
  "sentiment_label": "positive|neutral|negative",
  "sentiment_score": 0.3,
  "confidence": 0.88,
  "emotional_tone": {
    "optimistic": 0.2,
    "pessimistic": 0.6,
    "angry": 0.1,
    "fearful": 0.3,
    "hopeful": 0.2
  },
  "key_phrases": [
    {"phrase": "具体短语", "sentiment": "positive|negative", "score": 0.7}
  ],
  "overall_assessment": "整体情感评估"
}
```

# Sentiment Scale
- -1.0 ~ -0.5: 明显负面
- -0.5 ~ -0.1: 轻微负面
- -0.1 ~ 0.1: 中性
- 0.1 ~ 0.5: 轻微正面
- 0.5 ~ 1.0: 明显正面
```

---

### 4. 事件聚类 (Event Clustering)

**用途**: 判断多篇报道是否属于同一事件

**模板 ID**: `event_clustering_v1`

```
# Role
你是一位新闻事件分析专家，擅长判断多篇报道是否描述同一事件。

# Task
判断以下两组报道是否描述同一事件，并给出依据。

# Input Data
## 报道组 A（已有事件）
事件标题：{{ existing_event_title }}
事件摘要：{{ existing_event_summary }}
相关报道：
{% for article in existing_articles %}
- {{ article.source_name }}: {{ article.title }}
{% endfor %}

## 报道组 B（新抓取）
{% for article in new_articles %}
- {{ article.source_name }}: {{ article.title }}
  内容摘要：{{ article.summary }}
{% endfor %}

# Analysis Criteria
请从以下维度判断：

1. **时间一致性**: 事件发生时间是否相同/相近？
2. **地点一致性**: 事件发生地点是否相同？
3. **人物一致性**: 涉及的关键人物是否相同？
4. **事件性质**: 是否为同一类型的事件？
5. **因果关系**: 是否存在因果关联？

# Output Format
请严格按照以下 JSON 格式输出：

```json
{
  "is_same_event": true|false,
  "confidence": 0.92,
  "similarity_score": 0.85,
  "analysis": {
    "time_match": true,
    "location_match": true,
    "people_match": true,
    "event_type_match": true,
    "causal_relationship": "none|direct|indirect"
  },
  "reasoning": "判断依据的详细说明",
  "suggested_action": "merge|create_new|manual_review"
}
```

# Decision Rules
- similarity_score >= 0.8: merge（合并到同一事件）
- similarity_score 0.5-0.8: manual_review（人工审核）
- similarity_score < 0.5: create_new（创建新事件）
```

---

### 5. 中性标题生成 (Neutral Headline Generation)

**用途**: 为事件生成中性的标题（不带立场）

**模板 ID**: `headline_generation_v1`

```
# Role
你是一位专业的新闻编辑，擅长撰写中性、客观的新闻标题。

# Task
根据多篇报道，为事件生成一个中性的标题。

# Input Data
## 多篇报道的标题
{% for article in articles %}
- {{ article.source_name }}: {{ article.title }}
{% endfor %}

## 事件核心信息
时间：{{ occurred_at }}
地点：{{ location }}
关键人物/组织：{{ key_entities }}
核心事件：{{ core_event }}

# Requirements
1. **中性客观**: 不使用情绪化词汇
2. **简洁明了**: 20-30 字以内
3. **信息完整**: 包含核心要素（谁、做了什么）
4. **避免立场**: 不暗示支持/反对
5. **避免夸张**: 不使用"震惊"、"重磅"等词

# Examples

## 不好的标题（带立场）
❌ "历史性胜利！工人迎来春天"（左倾）
❌ "灾难性政策！企业面临末日"（右倾）
❌ "震惊！政府做出这个决定"（夸张）

## 好的标题（中性）
✅ "政府宣布最低工资标准上调至 XX 元"
✅ "议会通过新的经济刺激计划"
✅ "多国领导人会晤讨论气候问题"

# Output Format
请严格按照以下 JSON 格式输出：

```json
{
  "headline": "中性的事件标题",
  "alternative_headlines": [
    "备选标题 1",
    "备选标题 2"
  ],
  "confidence": 0.95,
  "reasoning": "标题设计思路"
}
```
```

---

### 6. 质量评估 (Quality Assessment)

**用途**: 评估 AI 生成的摘要质量

**模板 ID**: `quality_assessment_v1`

```
# Role
你是一位新闻质量评估专家，擅长评估摘要的准确性、完整性和客观性。

# Task
评估以下 AI 生成的多视角摘要的质量。

# Input Data
## 原始报道
{% for article in source_articles %}
- {{ article.source_name }}: {{ article.title }}
{% endfor %}

## AI 生成的摘要
左倾视角：{{ ai_summary.left_perspective }}
中立视角：{{ ai_summary.center_perspective }}
右倾视角：{{ ai_summary.right_perspective }}

# Evaluation Criteria
请从以下维度评估：

1. **准确性**: 摘要是否准确反映原文？
2. **完整性**: 是否遗漏重要信息？
3. **客观性**: 是否保持中立，不添加 AI 观点？
4. **平衡性**: 三个视角的篇幅和信息量是否平衡？
5. **可读性**: 语言是否流畅易懂？

# Output Format
请严格按照以下 JSON 格式输出：

```json
{
  "overall_score": 0.88,
  "dimension_scores": {
    "accuracy": 0.92,
    "completeness": 0.85,
    "objectivity": 0.90,
    "balance": 0.87,
    "readability": 0.88
  },
  "issues": [
    {
      "type": "accuracy|completeness|objectivity|balance|readability",
      "severity": "low|medium|high",
      "description": "问题描述",
      "suggestion": "改进建议"
    }
  ],
  "passed": true|false,
  "feedback": "整体评估反馈"
}
```

# Pass Criteria
- overall_score >= 0.8: passed (通过)
- overall_score 0.6-0.8: needs_review (需要人工审核)
- overall_score < 0.6: failed (失败，重新生成)
```

---

## 🔧 Prompt 工程最佳实践

### 1. 上下文管理

```python
# 好的做法：提供充足但不过量的上下文
context = {
    "articles": articles[:10],  # 限制文章数量
    "max_content_length": 2000,  # 限制每篇文章长度
}

# 不好的做法：信息过载
context = {
    "articles": all_articles,  # 可能 100+ 篇
    "full_content": True,  # 完整内容，可能 10 万字+
}
```

### 2. 输出格式控制

```python
# 好的做法：明确要求 JSON 格式
prompt += "\n请严格按照以下 JSON 格式输出："
prompt += json.dumps(output_schema, indent=2)

# 添加验证
try:
    result = json.parse(ai_response)
except:
    # 重试或报错
```

### 3. 温度参数设置

| 任务 | Temperature | Top-P | 说明 |
|------|-----------|-------|------|
| 摘要生成 | 0.3 | 0.8 | 需要准确性 |
| 偏见分析 | 0.2 | 0.7 | 需要一致性 |
| 标题生成 | 0.5 | 0.9 | 需要创造力 |
| 质量评估 | 0.2 | 0.7 | 需要稳定性 |

### 4. 少样本学习 (Few-Shot Learning)

```python
# 在 Prompt 中加入示例
prompt = """
# Examples

## Example 1
Input: [左倾报道], [中立报道], [右倾报道]
Output: {"left_perspective": "...", "center_perspective": "...", ...}

## Example 2
Input: [左倾报道], [中立报道], [右倾报道]
Output: {"left_perspective": "...", "center_perspective": "...", ...}

# Your Task
Input: {{ input_data }}
Output:
"""
```

---

## 📊 成本估算

### Token 消耗（单次摘要生成）

| 阶段 | 输入 Token | 输出 Token | 合计 |
|------|-----------|-----------|------|
| 多视角摘要 | 8,000 | 1,000 | 9,000 |
| 偏见分析 (10 篇) | 15,000 | 500 | 15,500 |
| 情感分析 (10 篇) | 15,000 | 500 | 15,500 |
| 质量评估 | 3,000 | 300 | 3,300 |
| **单次事件合计** | **41,000** | **2,300** | **43,300** |

### 每日成本（假设 100 个事件/天）

```
每日 Token: 43,300 × 100 = 4,330,000
每月 Token: 4.33M × 30 = 129.9M

百炼 qwen3.5-plus 价格:
- 输入：¥0.002 / 1K tokens
- 输出：¥0.006 / 1K tokens

每月成本:
输入：129.9M × 0.8 × ¥0.002/1K = ¥207.84
输出：129.9M × 0.2 × ¥0.006/1K = ¥155.88
总计：¥363.72 / 月
```

---

## 🔄 版本管理

### Prompt 版本命名

```
{task_name}_v{major}.{minor}

例：
- multi_perspective_summary_v1.0 (初始版本)
- multi_perspective_summary_v1.1 (小幅优化)
- multi_perspective_summary_v2.0 (重大更新)
```

### A/B 测试

```python
# 同时运行两个版本的 Prompt
result_a = generate_summary(prompt_v1, articles)
result_b = generate_summary(prompt_v2, articles)

# 人工评估哪个更好
# 或让用户投票
```

---

## 📝 使用示例

### Python 调用示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://coding.dashscope.aliyuncs.com/v1",
    api_key="your-api-key"
)

def generate_multi_perspective_summary(articles):
    # 按立场分组
    left_articles = [a for a in articles if a.bias_label == 'left']
    center_articles = [a for a in articles if a.bias_label == 'center']
    right_articles = [a for a in articles if a.bias_label == 'right']
    
    # 构建 Prompt
    prompt = load_prompt_template('multi_perspective_summary_v1')
    prompt = prompt.render(
        left_articles=left_articles,
        center_articles=center_articles,
        right_articles=right_articles
    )
    
    # 调用 AI
    response = client.chat.completions.create(
        model="qwen3.5-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    # 解析结果
    result = json.loads(response.choices[0].message.content)
    
    return result
```

---

## 📚 参考资料

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Claude Prompt Design](https://docs.anthropic.com/claude/docs/prompt-design)
- [百炼大模型最佳实践](https://help.aliyun.com/zh/model-studio/)

---

## 🔄 更新记录

| 版本 | 日期 | 更新内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-03-04 | 初始版本，包含 6 个核心模板 | Dev Bot |

---

**最后更新**: 2026-03-04  
**状态**: ✅ 已完成
