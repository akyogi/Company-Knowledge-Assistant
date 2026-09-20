import ollama
from llmmodels.VectorDB import VectorDB


class TextProcessor :
    path_to_file :str = None
    name_file : str = None
    collection = VectorDB()


    def __init__(self ,path_to_file:str, name_file :str):
        self.path_to_file = path_to_file
        self.name_file=name_file

    def chunk_file_data(self,overall_text:str) -> list[str] :
        print("....Running chunk_file_data.....")
        text = (overall_text or "").strip()
        if not text:
            return []
        chunk_size = 1000
        chunks = [
            text[i: i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]

        return chunks

    def embed_and_index_pdf(self,chunks:list[str]):
        if not chunks:
            raise ValueError("No text chunks to index. The PDF may have no extractable text.")

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for i, ch in enumerate(chunks):
            response = ollama.embeddings(model="nomic-embed-text:latest", prompt=ch)
            embeddings.append(response["embedding"])
            ids.append(f"{self.name_file}_{i}")  # unique ID per chunk
            documents.append(ch)
            metadatas.append({"filename": self.name_file, "path": self.path_to_file, "chunk": i})

        # Add all chunks to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        print(f"Indexed {self.name_file} successfully.")

    def process_whole_pdf(self, data:str):
        print("Processing PDF..............")
        chunks = self.chunk_file_data(data)
        self.embed_and_index_pdf(chunks)

