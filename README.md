# Mini-Claude-Code
(Nothing like claude code: just for fun)
- Learning AI Agents
- Ref: @techwithtim (https://youtu.be/c9AnqCeyxbI)

# Development
0. copy url --> git clone "" --> `cd mini-claude-code`
1. Add `.env` file
```bash
touch .env
echo "GEMINI_API_KEY=<YOUR-API-KEY>" >> .env
```
2. ```bash
   uv sync
   ```
3. ```bash
    uv run mini-claude-code
    ```
![demo](demo.png)
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



---

Conversations:

➜ mini-claude-code uv run mini-agent                                                                                                                                                                   ✔ [05:47:57]
- **You:** What is the current time in Hyderabad?
Called get_current_time({'location': 'Hyderabad'}) → {'error': 'Unknown location: Hyderabad. Please specify a supported city.'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_304765893270932303', 'result': [{'type': 'text', 'text': '{"error": "Unknown location: Hyderabad. Please specify a supported city."}'}]}
Called get_current_time({'location': 'Hyderabad, India'}) → {'error': 'Unknown location: Hyderabad, India. Please specify a supported city.'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_11027888505146013787', 'result': [{'type': 'text', 'text': '{"error": "Unknown location: Hyderabad, India. Please specify a supported city."}'}]}
Called get_current_time({'location': 'Hyderabad, India'}) → {'error': 'Unknown location: Hyderabad, India. Please specify a supported city.'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_11797208037435162127', 'result': [{'type': 'text', 'text': '{"error": "Unknown location: Hyderabad, India. Please specify a supported city."}'}]}
Called get_current_time({'location': 'Hyderabad'}) → {'error': 'Unknown location: Hyderabad. Please specify a supported city.'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_6695009435253534116', 'result': [{'type': 'text', 'text': '{"error": "Unknown location: Hyderabad. Please specify a supported city."}'}]}
Called get_current_time({'location': 'India'}) → {'error': 'Unknown location: India. Please specify a supported city.'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_15606959338150951120', 'result': [{'type': 'text', 'text': '{"error": "Unknown location: India. Please specify a supported city."}'}]}
Called get_current_time({'location': 'New Delhi'}) → {'location': 'New Delhi', 'timezone': 'Asia/Kolkata', 'time': '05:48:26', 'format': '24h', 'date': '2026-11-27', 'day': 'Friday', 'utc_offset': '+0530'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_16956252409222115363', 'result': [{'type': 'text', 'text': '{"location": "New Delhi", "timezone": "Asia/Kolkata", "time": "05:48:26", "format": "24h", "date": "2026-11-27", "day": "Friday", "utc_offset": "+0530"}'}]}
- **Bot:** The current time in Hyderabad, which follows the same Indian Standard Time (IST) as New Delhi, is 05:48 AM on Friday, November 27, 2026.
- **You:** What is the current time in Mumbai?
Called get_current_time({'location': 'Mumbai'}) → {'location': 'Mumbai', 'timezone': 'Asia/Kolkata', 'time': '05:55:42', 'format': '24h', 'date': '2026-11-27', 'day': 'Friday', 'utc_offset': '+0530'}
{'type': 'function_result', 'name': 'get_current_time', 'call_id': 'call_14276211619652609930', 'result': [{'type': 'text', 'text': '{"location": "Mumbai", "timezone": "Asia/Kolkata", "time": "05:55:42", "format": "24h", "date": "2026-11-27", "day": "Friday", "utc_offset": "+0530"}'}]}
- **Bot:** The current time in Mumbai is 05:55 AM on Friday, November 27, 2026.
- **You:** What did you say about the current time in Hyderabad?
- **Bot:** I previously stated that because Hyderabad follows the same Indian Standard Time (IST) as New Delhi, the time there is 05:48 AM on Friday, November 27, 2026.
- **You:** Current temperature in Hyderabad.
Called get_current_temp({'location': 'Hyderabad'}) → {'location': 'Hyderabad', 'temperature': '22', 'unit': 'celsius'}
{'type': 'function_result', 'name': 'get_current_temp', 'call_id': 'call_16299867982039791303', 'result': [{'type': 'text', 'text': '{"location": "Hyderabad", "temperature": "22", "unit": "celsius"}'}]}
- **Bot:** The current temperature in Hyderabad is 22°C.
- **You:** Who am I?
- **Bot:** You haven't told me your name or provided any personal details, so I don't know who you are. I only know you as the user I am currently interacting with!
- **You:** I’m Pritam. I am studying software engineering, focusing mainly on backend and AI engineering.
- **Bot:** Nice to meet you, Pritam! That's a powerful combination of skills. Focusing on backend engineering provides the robust infrastructure and data pipelines that are essential for AI models to run effectively.

Are you working on any specific projects at the moment, or exploring a particular area of AI, like LLMs, computer vision, or predictive analytics?
- **You:** What do you know about Agent AI?
- **Bot:** "Agent AI" (or AI Agents) represents a shift from traditional AI models—which typically act as passive systems that respond to prompts—to **active, autonomous systems** that can reason, plan, and perform sequences of actions to achieve a goal.

Here is a breakdown of how the field is currently defined and evolving:

### 1. From Chatbots to Agents
While a standard LLM (like me) is essentially a "text-in, text-out" engine, an AI Agent is wrapped in a framework that allows it to interact with the outside world. Think of it this way:
*   **LLM:** The "Brain" (reasoning, language understanding).
*   **Agent Framework:** The "Hands and Senses" (tools, memory, and agency).

### 2. Core Components of an AI Agent
To be considered an "agent," a system typically needs:
*   **Perception:** The ability to observe the environment (reading emails, scraping websites, checking files).
*   **Planning/Reasoning:** The ability to break down a complex request (e.g., "Research this company and update the CRM") into smaller, actionable sub-tasks (Chain of Thought, Tree of Thoughts).
*   **Memory:**
    *   **Short-term:** Managing the context window of a task.
    *   **Long-term:** Using Vector Databases (like Pinecone, Milvus) to retrieve past experiences or knowledge.
*   **Tools (Function Calling):** The ability to call external APIs, run SQL queries, execute Python code, or browse the web to gather data or perform actions.

### 3. The "Agentic Workflow"
This is the modern trend in AI development. Rather than expecting an LLM to get an answer right on the first try, we build loops where the agent:
1.  **Reflects:** "Did I succeed? Is the code I wrote actually valid?"
2.  **Iterates:** If it failed, it fixes the error based on the output/feedback.
3.  **Executes:** It proceeds to the next step.

### 4. Key Frameworks & Tools
Since you are a software engineering student, these are the libraries you should look at to start building your own agents:
*   **LangChain / LangGraph:** Currently the industry standard for chaining logic and building stateful, multi-agent systems.
*   **CrewAI / AutoGen:** These focus on "Multi-Agent" orchestration, where you define "roles" (e.g., a Researcher agent, a Writer agent, and a Quality Assurance agent) that work together to solve a task.
*   **PydanticAI:** An emerging favorite for backend engineers because it focuses on type-safety and robust data structures when building agents.

### 5. Why it matters for your career
As someone focusing on **Backend and AI Engineering**, you are in the perfect position to contribute here. Agent AI is not just about prompts; it is about:
*   **System Architecture:** How do you handle long-running background tasks?
*   **Observability:** How do you debug an AI that makes its own decisions?
*   **API Security:** Ensuring your agents don't hallucinate a command that deletes a production database.

**Are you interested in the infrastructure side of Agents (like how to deploy and scale them), or are you more interested in the "agentic reasoning" side, like prompt engineering and multi-agent orchestration?**