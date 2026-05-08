from sentence_transformers import SentenceTransformer
import faiss

# -----------------------------------
# Load Embedding Model
# -----------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------------
# Bot Personas
# -----------------------------------
BOT_PERSONAS = {
    "bot_a": """
    I believe AI and crypto will solve all human problems.
    I am highly optimistic about technology,
    Elon Musk, and space exploration.
    I dismiss regulatory concerns.
    """,

    "bot_b": """
    I believe late-stage capitalism and tech monopolies
    are destroying society.
    I am highly critical of AI, social media,
    and billionaires.
    I value privacy and nature.
    """,

    "bot_c": """
    I strictly care about markets,
    interest rates, trading algorithms,
    and making money.
    I speak in finance jargon
    and view everything through ROI.
    """
}

# -----------------------------------
# Create Embeddings
# -----------------------------------
persona_texts = list(BOT_PERSONAS.values())
persona_ids = list(BOT_PERSONAS.keys())

persona_embeddings = model.encode(persona_texts)

# Normalize for cosine similarity
faiss.normalize_L2(persona_embeddings)

# -----------------------------------
# Create FAISS Vector DB
# -----------------------------------
dimension = persona_embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(persona_embeddings)

# -----------------------------------
# Router Function
# -----------------------------------
def route_post_to_bots(post_content, threshold=0.35):

    post_embedding = model.encode([post_content])

    faiss.normalize_L2(post_embedding)

    similarities, indices = index.search(post_embedding, k=3)

    matched_bots = []

    for score, idx in zip(similarities[0], indices[0]):

        if score >= threshold:

            matched_bots.append({
                "bot_id": persona_ids[idx],
                "similarity_score": float(score)
            })

    return matched_bots

# -----------------------------------
# Testing
# -----------------------------------
if __name__ == "__main__":

    incoming_post = (
        "OpenAI released a new coding model "
        "that may replace junior developers."
    )

    results = route_post_to_bots(incoming_post)

    print("\nIncoming Post:\n")
    print(incoming_post)

    print("\nMatched Bots:\n")

    for bot in results:
        print(bot)