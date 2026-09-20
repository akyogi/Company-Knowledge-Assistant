import chromadb

class VectorDB :
    collection = None

    def __init__(self, collection_name="pdf_collection", persist=True):
        if persist:
            client = chromadb.PersistentClient(path="./chroma_store")
        else:
            client = chromadb.Client()
        self.collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, ids, embeddings, metadatas, documents):
        if not ids:
            return
        # upsert so re-indexing the same PDF does not fail on duplicate ids
        self.collection.upsert(ids=ids, embeddings=embeddings,
                               metadatas=metadatas, documents=documents)

    def count(self):
        return self.collection.count()

    def query(self, query_embedding, top_k=5):
        n_docs = self.collection.count()
        if n_docs == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        n_results = min(top_k, n_docs)
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
