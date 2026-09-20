from llmmodels.VectorDB import VectorDB
from llmmodels.LLMModel import LLMModel
from llmmodels.EmdebModel import EmbedModel


class QueryProcessor:
    """
    Handles user queries:
    - Converts query to embedding
    - Retrieves relevant document chunks
    - Constructs prompt
    - Generates LLM response with citations
    """

    def __init__(self):
        self.vector_db = VectorDB()
        self.embed_model = EmbedModel()
        self.llm_model = LLMModel()

    def vectorize_query(self, query_text):
        """Generate embedding for user query."""
        query_embedding = self.embed_model.embed(query_text)
        return query_embedding

    def retrieve_context(self, query_embedding, top_k=5, threshold=0.85, file_name=None):
        where = {"filename": file_name} if file_name else None
        results = self.vector_db.query(query_embedding, top_k=top_k, where=where)
        chunks = results["documents"][0] or []
        metadata = results["metadatas"][0] or []
        distances = results["distances"][0] or []

        filtered_chunks = []
        filtered_metadata = []
        for ch, meta, dist in zip(chunks, metadata, distances):
            # Cosine distance: 0 is identical, 1 is orthogonal.
            # A generic question like "what is this document about" often
            # scores worse than 0.3 against specific PDF text.
            if dist < threshold:
                filtered_chunks.append(ch)
                filtered_metadata.append(meta)

        # Always keep the nearest neighbors so the LLM has source text.
        if not filtered_chunks and chunks:
            return chunks, metadata

        return filtered_chunks, filtered_metadata

    def construct_prompt(self, query_text, retrieved_chunks, retrieved_metadata):
        context_text = "\n\n".join(retrieved_chunks)

        # Optional: include citations from metadata
        citations = "\n".join([
            f"Source: {meta['filename']} (chunk {i})"
            for i, meta in enumerate(retrieved_metadata)
        ])

        prompt = (
            f"Answer the following question using only the context below.\n"
            f"If the answer is not found, say 'I don't know.'\n"
            f"Always cite the source document.\n\n"
            f"Context:\n{context_text}\n\n"
            f"{citations}\n\n"
            f"Question: {query_text}\n"
            f"Answer:"
        )
        return prompt

    def generate_response(self, prompt):
        """Send prompt to LLM and get response."""
        response = self.llm_model.generate(prompt)
        return response

    def process_query(self, query_text, file_name=None):
        """Main pipeline for handling a user query against already indexed PDFs."""
        where = {"filename": file_name} if file_name else None
        if self.vector_db.count(where=where) == 0:
            return None, {"chunks": [], "metadata": []}

        query_embedding = self.vectorize_query(query_text)
        retrieved_chunks, retrieve_metadata = self.retrieve_context(
            query_embedding, file_name=file_name
        )
        prompt = self.construct_prompt(query_text, retrieved_chunks, retrieve_metadata)
        response = self.generate_response(prompt)
        return response, {"chunks": retrieved_chunks, "metadata": retrieve_metadata}
