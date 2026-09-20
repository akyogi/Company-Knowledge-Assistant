import ollama

class EmbedModel:
    def __init__(self, model_name="nomic-embed-text:latest"):
        self.model_name = model_name

    def embed(self, text):
        # Conceptual call to Ollama embeddings API
        response = ollama.embeddings(model=self.model_name, prompt=text)
        return response["embedding"]
