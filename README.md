<img width="1536" height="314" alt="image" src="https://github.com/user-attachments/assets/dd40d2db-61da-47c7-9284-80ff6f185008" /># Company Knowledge Assistant

A local RAG (retrieval-augmented generation) app: upload a PDF, index its text, then ask questions. Answers come from retrieved chunks plus a local LLM, with source filenames shown in the UI.

## How it works

1. **Upload** — `POST /home/upload` accepts a PDF. Text is extracted with `pypdf`. Scanned PDFs with no text layer are rejected.
2. **Chunk** — The extracted text is split into 1000-character pieces (`TextProcessor`).
3. **Embed and store** — Each chunk is embedded with Ollama (`nomic-embed-text:latest`) and stored in a persistent Chroma collection (`pdf_collection` under `./chroma_store`). Re-uploading the same filename replaces the previous chunks for that file. Metadata includes `filename`, `path`, and chunk index.
4. **Ask** — `POST /home/ask` embeds the question, retrieves the nearest chunks (cosine similarity, top 5), and prompts `llama3.2:latest` to answer **only from that context**. If nothing is indexed yet, the API returns an error telling you to upload first.
5. **UI** — Open `/home/ask` to upload a PDF and ask questions. The page shows the answer and source filenames.

Indexed data lives on disk in `chroma_store/`, so you can ask again later without re-uploading (until you delete that folder).

## Stack

| Piece | Choice |
| --- | --- |
| API | FastAPI (`main.py` + `routers/home.py`) |
| UI | Jinja template `templates/ask.html` |
| Embeddings | Ollama `nomic-embed-text:latest` |
| LLM | Ollama `llama3.2:latest` |
| Vector store | ChromaDB (cosine space) |

## Prerequisites

- Python 3
- [Ollama](https://ollama.com) running locally
- Pull the models used by the app:

```bash
ollama pull nomic-embed-text:latest
ollama pull llama3.2:latest
```

Python packages used by the app: `fastapi`, `uvicorn`, `pypdf`, `chromadb`, `ollama`, `jinja2`, `python-multipart`.

## Run

From the project root (so `./chroma_store` is created in the right place):

```bash
uvicorn main:app --reload
```

Then open **http://127.0.0.1:8000/home/ask**.

## API

**Upload a PDF**

```http
POST /home/upload
Content-Type: multipart/form-data
```

Form field: `file` (PDF). Response `202` with `message` and `file_name`.

**Ask a question**

```http
POST /home/ask
Content-Type: application/x-www-form-urlencoded
```

Form fields: `query` (required), `file_name` (optional; limits search to that indexed PDF). Response `202` with `answer` and `sources` (`chunks` and `metadata`).

**Page**

```http
GET /home/ask
```

## Project layout

```
main.py                 FastAPI app; mounts the home router
routers/home.py         Upload, ask, and page routes
templates/ask.html      Upload + Q&A UI
tools/TextProcessor.py  Chunk, embed, index PDFs
tools/QueryProcessor.py Retrieve context and call the LLM
llmmodels/EmdebModel.py Query embeddings via Ollama
llmmodels/LLMModel.py   Answer generation via Ollama
llmmodels/VectorDB.py   Chroma client (persistent)
```

##### Upload PDF
<img width="1420" height="401" alt="image" src="https://github.com/user-attachments/assets/080d0140-a5e3-474c-8036-fbcac80e07c7" />

##### Ask Query
<img width="1420" height="401" alt="image" src="https://github.com/user-attachments/assets/eaafff3c-184e-49e8-ab30-7911284798fa" />

#### Sample UI 
a) Upload PDFs : 
<img width="1525" height="187" alt="image" src="https://github.com/user-attachments/assets/24216ed9-8852-4b12-8aae-c69aa152ebba" />

<img width="1517" height="203" alt="image" src="https://github.com/user-attachments/assets/90a6ca9e-9cf5-497c-bc14-e2a818d36e43" />

b) Ask queries : 
<img width="1537" height="274" alt="image" src="https://github.com/user-attachments/assets/09e4eae4-a45d-40ae-836a-6239e165f9f0" />

<img width="1526" height="327" alt="image" src="https://github.com/user-attachments/assets/1b93eb2f-b018-4c2e-b640-60ce39e67cab" />

<img width="1520" height="368" alt="image" src="https://github.com/user-attachments/assets/5e69d2d9-b1f9-4ba8-b7f1-c4b147a0afbd" />











