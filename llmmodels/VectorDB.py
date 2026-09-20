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

    def count(self, where=None):
        if not where:
            return self.collection.count()
        existing = self.collection.get(where=where, include=[])
        return len(existing.get("ids") or [])

    def delete_by_filename(self, filename: str):
        if self.count(where={"filename": filename}):
            self.collection.delete(where={"filename": filename})

    def query(self, query_embedding, top_k=5, where=None):
        n_docs = self.count(where=where)
        if n_docs == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        n_results = min(top_k, n_docs)
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)
