import os
import asyncpg
from .embeddings import get_embedding
import openai

async def retrieve_context(query: str, top_k: int, session_id: str, user_id: str):
    embedding = await get_embedding(query)
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        rows = await conn.fetch(
            """
            SELECT chunk_text, metadata, embedding <-> $1 AS similarity
            FROM document_chunks
            WHERE session_id = $2 AND user_id = $3
            ORDER BY similarity ASC
            LIMIT $4
            """,
            embedding, session_id, user_id, top_k
        )
        return [{'chunk_text': row['chunk_text'], 'metadata': row['metadata']} for row in rows]
    finally:
        await conn.close()

async def answer_question(query: str, session_id: str, user_id: str) -> dict:
    context_chunks = await retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)
    if not context_chunks:
        return {'answer': 'No relevant information found.', 'sources': []}

    prompt = "Answer the following question based on the provided context:\n\n"
    for chunk in context_chunks:
        prompt += f"Context: {chunk['chunk_text']}\n\n"
    prompt += f"Question: {query}\n\nProvide a concise answer with citations."

    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role': 'user', 'content': prompt}]
    )
    answer = response.choices[0].message.content

    sources = [{'filename': chunk['metadata']['source_filename'], 'location': chunk['metadata']['page_or_row']} for chunk in context_chunks]
    return {'answer': answer, 'sources': sources}