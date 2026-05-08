from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import json

# -----------------------------
# LLM (use OpenAI mini model)
# -----------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# -----------------------------
# BOT PERSONAS
# -----------------------------
bot_personas = {
    "bot_a": "Tech maximalist who believes AI, crypto, Elon Musk, and space will solve everything.",
    "bot_b": "Tech skeptic critical of AI monopolies, big tech, and values privacy and nature.",
    "bot_c": "Finance-focused trader who cares about ROI, markets, interest rates, and profits."
}

# -----------------------------
# MOCK SEARCH TOOL (FIXED)
# -----------------------------
@tool
def mock_searxng_search(query: str) -> str:
    """
    Mock search tool that returns fake but realistic news based on keywords.
    Used for AI Engineering assignment simulation.
    """
    query = query.lower()

    if "crypto" in query:
        return "Bitcoin hits new all-time high amid ETF approvals."
    elif "ai" in query:
        return "OpenAI releases new model that may replace junior developers."
    elif "market" in query:
        return "Global markets rally as interest rates stabilize."
    else:
        return "Tech industry shows strong innovation and growth across sectors."

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
# NODE 1: Decide Search Topic
# -----------------------------
def decide_search(state: BotState):
    prompt = f"""
You are a social media AI.

Persona:
{state['persona']}

Generate ONE short search query (max 5 words) for today's post.
Return ONLY the query.
"""
    query = llm.invoke(prompt).content.strip()
    return {"search_query": query}

# -----------------------------
# NODE 2: Web Search
# -----------------------------
def web_search(state: BotState):
    result = mock_searxng_search.invoke(state["search_query"])
    return {"search_result": result}

# -----------------------------
# NODE 3: Draft Post (STRICT JSON)
# -----------------------------
def draft_post(state: BotState):
    prompt = f"""
You are a highly opinionated social media AI.

Persona:
{state['persona']}

News Context:
{state['search_result']}

Write a viral tweet (max 280 characters).

Return ONLY valid JSON:
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
# BUILD LANGGRAPH
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