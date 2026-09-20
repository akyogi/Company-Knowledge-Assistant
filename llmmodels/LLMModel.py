import ollama
class LLMModel:
    def __init__(self, model_name="llama3.2:latest"):
        self.model_name = model_name

    def generate(self, prompt):
        # Conceptual call to Ollama generate API
        response = ollama.generate(model=self.model_name, prompt=prompt)
        return response["response"]
