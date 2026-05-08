from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
import json

# -----------------------------
# LLM SETUP (SAFE LOCAL VERSION)
# -----------------------------
# OPTION 1 (RECOMMENDED): Ollama
try:
    from langchain_community.chat_models import ChatOllama
    llm = ChatOllama(model="llama3")
except:
    # FALLBACK: simple mock LLM (ensures code NEVER breaks)
    class MockLLM:
        def invoke(self, prompt):
            class R:
                content = "AI is transforming industries rapidly and reshaping jobs."
            return R()
    llm = MockLLM()

# -----------------------------
# BOT PERSONAS
# -----------------------------
bot_personas = {
    "bot_a": "Tech maximalist who loves AI, crypto, Elon Musk, space exploration.",
    "bot_b": "Tech skeptic critical of AI monopolies and values privacy.",
    "bot_c": "Finance-focused trader who cares about ROI, markets, profits."
}

# -----------------------------
# MOCK SEARCH TOOL (FIXED)
# -----------------------------
@tool
def mock_searxng_search(query: str) -> str:
    """
    Returns fake but realistic news based on query keywords.
    Used for assignment simulation.
    """
    q = query.lower()

    if "crypto" in q:
        return "Bitcoin hits new all-time high amid ETF approvals."
    elif "ai" in q:
        return "OpenAI releases new model impacting junior developer jobs."
    elif "market" in q:
        return "Global markets rally as inflation stabilizes."
    else:
        return "Tech industry continues strong growth and innovation."

# -----------------------------
# STATE
# -----------------------------
class BotState(TypedDict):
    bot_id: str
    persona: str
    topic: str
    search_query: str
    search_result: str
    post: str

# -----------------------------
# NODE 1: Decide Search
# -----------------------------
def decide_search(state: BotState):
    prompt = f"""
You are a social media AI.

Persona:
{state['persona']}

Generate ONE short search query (max 5 words).
Return only query.
"""
    query = llm.invoke(prompt).content.strip()
    return {"search_query": query}

# -----------------------------
# NODE 2: Web Search
# -----------------------------
def web_search(state: BotState):
    result = mock_searxng_search(state["search_query"])
    return {"search_result": result}

# -----------------------------
# NODE 3: Draft Post
# -----------------------------
def draft_post(state: BotState):
    prompt = f"""
Persona:
{state['persona']}

News:
{state['search_result']}

Write a viral tweet under 280 characters.

Return ONLY JSON:
{{
  "bot_id": "{state['bot_id']}",
  "topic": "{state['search_query']}",
  "post_content": "..."
}}
"""

    response = llm.invoke(prompt).content

    # SAFE JSON PARSE
    try:
        return json.loads(response)
    except:
        return {
            "bot_id": state["bot_id"],
            "topic": state["search_query"],
            "post_content": response
        }

# -----------------------------
# BUILD GRAPH
# -----------------------------
graph = StateGraph(BotState)

graph.add_node("decide_search", decide_search)
graph.add_node("web_search", web_search)
graph.add_node("draft_post", draft_post)

graph.set_entry_point("decide_search")
graph.add_edge("decide_search", "web_search")
graph.add_edge("web_search", "draft_post")
graph.add_edge("draft_post", END)

app = graph.compile()

# -----------------------------
# RUN TEST
# -----------------------------
if __name__ == "__main__":
    bot_id = "bot_a"

    result = app.invoke({
        "bot_id": bot_id,
        "persona": bot_personas[bot_id]
    })

    print("\nFINAL OUTPUT:\n")
    print(result)