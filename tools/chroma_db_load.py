import chromadb

# Initialize the client and collection once at the module level
client = chromadb.PersistentClient(path="./pdf_db")
collection = client.get_or_create_collection(name="pdf_document_chunks")

def get_collection():
    """Returns the live collection instance."""
    return collection