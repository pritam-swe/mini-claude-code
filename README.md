# Mini-Claude-Code
(Nothing like claude code: just for fun)
- Learning AI Agents
- Ref: @techwithtim (https://youtu.be/c9AnqCeyxbI)

## Learnings

### 1. The two Gemini APIs
#### A. Generate Content API
This is the traditional Gemini API interface.
```py
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Explain how AI works"
)

print(response.text)
```

Its primary responsibility is straightforward:
- You provide content.
- Gemini generates a response.
- You receive a response object.
It supports much more than simple text generation, including multi-turn conversations, system instructions, structured output and tool use.
---
#### B. Interactions API
This is Google's newer unified interface for interacting with models and agents.

```python
interaction = client.interactions.create(
    model="gemini-3.1-flash-lite",
    input="Explain how AI works"
)

print(interaction.output_text)
```

It provides a more unified structure for:
- Model interactions.
- Multi-turn conversations.
- Tool orchestration.
- Agent workflows.
- Managing interaction state and continuation.
Think of it this way:
- generate_content() is a model-centric interface.
- interactions.create() is an interaction-centric interface.

> From June 2026, Google recommends the Interactions API for new projects. `generate_content()` is still supported, but Google now considers it the legacy interface.

---

## What we are doing??
A multi‑turn conversations.
- First, the jargon of the agent loop is *stateless*.
**Stateless**: Manage the conversation history on the client by passing all previous turns (`including intermediate model thought and tool steps`) in each request.
- Set `store=false` and manage conversation history on the client side. You must preserve and resend all model-generated steps (including thought and function_call steps) exactly as received.