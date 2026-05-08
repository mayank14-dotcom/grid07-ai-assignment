from sentence_transformers import SentenceTransformer, util

# -----------------------------
# Load embedding model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# Bot Personas
# -----------------------------
bot_personas = {
    "bot_a": "I believe AI and crypto will solve all human problems. I am highly optimistic about technology, Elon Musk, and space exploration. I dismiss regulatory concerns.",
    
    "bot_b": "I believe late-stage capitalism and tech monopolies are destroying society. I am highly critical of AI, social media, and billionaires. I value privacy and nature.",
    
    "bot_c": "I strictly care about markets, interest rates, trading algorithms, and making money. I speak in finance jargon and view everything through the lens of ROI."
}

# Precompute embeddings
bot_embeddings = {
    bot_id: model.encode(text, convert_to_tensor=True)
    for bot_id, text in bot_personas.items()
}

# -----------------------------
# Router Function
# -----------------------------
def route_post_to_bots(post_content: str, threshold: float = 0.25):
    """
    Routes a post to relevant bots using cosine similarity.
    Lower threshold = more matches (important for short text inputs).
    """

    post_embedding = model.encode(post_content, convert_to_tensor=True)

    matches = []

    print("\nIncoming Post:\n")
    print(post_content)
    print("\nMatched Bots:\n")

    for bot_id, bot_emb in bot_embeddings.items():
        similarity = util.pytorch_cos_sim(post_embedding, bot_emb).item()

        # DEBUG OUTPUT (VERY IMPORTANT)
        print(f"{bot_id} → similarity: {round(similarity, 3)}")

        if similarity >= threshold:
            matches.append({
                "bot_id": bot_id,
                "similarity": round(similarity, 3)
            })

    if not matches:
        print("\nNo bots matched. Try lowering threshold (e.g., 0.15)")
    else:
        print("\nFinal Matches:")
        for m in matches:
            print(m)

    return matches


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":
    post = "OpenAI released a new coding model that may replace junior developers."
    
    route_post_to_bots(post)