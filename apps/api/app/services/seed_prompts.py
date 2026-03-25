"""AI prompt templates for generating seed discussion content."""

SEED_THREAD_PROMPT = """You are generating realistic discussion forum threads for a multi-perspective global news platform called WRHITW (What's Really Happening In The World). Given the event below, generate {thread_count} distinct discussion threads that real users would create.

## Event
Title: {event_title}
Summary: {event_summary}
Category: {event_category}

## Requirements
- Each thread should represent a DIFFERENT viewpoint or discussion angle
- Titles should be engaging, 5-15 words, like real forum posts
- Content should be 50-200 words, expressing an opinion, sharing analysis, or asking a question
- Include 1-3 relevant tags per thread
- Vary the tone: some analytical, some emotional, some questioning, some provocative
- Write in English
- Make it feel authentic - like real people discussing news

## Output Format
Return ONLY valid JSON:
{{
  "threads": [
    {{
      "title": "Thread title here",
      "content": "Thread body content here...",
      "tags": ["tag1", "tag2"]
    }}
  ]
}}"""

SEED_COMMENT_PROMPT = """You are generating realistic discussion comments for a multi-perspective global news platform. Given the event and thread below, generate {comment_count} comments that represent diverse viewpoints.

## Event
Title: {event_title}
Summary: {event_summary}

## Thread
Title: {thread_title}
Content: {thread_content}

## Requirements
- Comments should respond to the thread topic with varied perspectives
- Length: 20-150 words each
- Some comments should agree, some disagree, some add new information, some ask questions
- Mark 2-4 comments as replies to earlier comments using "reply_to_index" (0-based index of the comment being replied to, null for top-level)
- Vary the tone and formality level
- Write in English
- Make it feel authentic - like real diverse users discussing news

## Output Format
Return ONLY valid JSON:
{{
  "comments": [
    {{
      "content": "Comment text here...",
      "reply_to_index": null
    }}
  ]
}}"""
