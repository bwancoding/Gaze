"""AI prompt templates for generating seed discussion content."""

SEED_THREAD_PROMPT = """Generate {thread_count} discussion threads for a news event on a global news forum.

## Event
Title: {event_title}
Summary: {event_summary}
Category: {event_category}

## Writing style — CRITICAL
You are writing AS different real people, not as an AI assistant. Follow these rules strictly:

- Write like actual internet users: some articulate, some blunt, some rambling
- NEVER use these AI patterns: "It's important to note", "Furthermore", "Additionally", "It's worth mentioning", "In conclusion", "That being said", "This raises important questions"
- NEVER hedge everything — real people have strong opinions and state them directly
- NEVER balance both sides in a single post — a real person picks a side or asks a genuine question
- Use contractions freely (don't, can't, won't, it's)
- Vary sentence length dramatically — mix short punchy sentences with longer ones
- Some posts should be slightly messy: incomplete thoughts, tangents, rhetorical questions
- Use informal punctuation sometimes: dashes, ellipses, ALL CAPS for emphasis
- Reference personal experience or specific details when possible ("I work in supply chain and...")
- Some threads should be provocative or frustrated, not just politely analytical

## Content rules
- Each thread = a DIFFERENT angle or viewpoint on the event
- Titles: 5-15 words, like real forum posts (questions, hot takes, observations)
- Content: 50-200 words per thread
- Include 1-3 relevant tags
- Write in English

## Output
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

SEED_COMMENT_PROMPT = """Generate {comment_count} comments replying to a discussion thread on a global news forum.

## Event
Title: {event_title}
Summary: {event_summary}

## Thread
Title: {thread_title}
Content: {thread_content}

## Writing style — CRITICAL
You are writing AS different real people, not as an AI assistant:

- Write like actual humans on the internet — varied education levels, backgrounds, and communication styles
- NEVER use: "It's important to note", "Furthermore", "Additionally", "That being said", "While I understand", "This raises questions about"
- NEVER make every comment perfectly balanced — most real people lean one way
- Some comments should be short and blunt (1-2 sentences). Some should be longer and passionate
- Use contractions, informal language, occasional typos or grammar quirks
- Some should disagree sharply, some should add personal anecdotes, some should be sarcastic
- Let some comments be slightly off-topic or tangential — that's how real discussions work
- Mix formality levels: some write like journalists, some like they're texting a friend
- Include the occasional emoji or internet shorthand sparingly (tbh, imo, smh)

## Content rules
- 20-150 words each
- Mark 2-4 comments as replies to earlier ones via "reply_to_index" (0-based, null for top-level)
- Write in English

## Output
Return ONLY valid JSON:
{{
  "comments": [
    {{
      "content": "Comment text here...",
      "reply_to_index": null
    }}
  ]
}}"""
