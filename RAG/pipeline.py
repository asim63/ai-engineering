import os
import json
from collections import defaultdict
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
from ollama import chat

from .config import RAGConfig
from .utils import clean_text, strip_think_tags


class RAGPipeline:
    def __init__(self, config: RAGConfig):
        self.config = config

        # Load models once at init
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.embedding_model
        )
        self.reranker = CrossEncoder(config.reranker_model)

        # These get populated when you load a PDF
        self.db = None
        self.parent_chunks = {}
        self.child_chunks_flat = []   # for BM25
        self.bm25 = None

    #  Document Loading 

    def load_pdf(self, path: str):
        """Load, clean, chunk, and store a PDF."""
        loader = PyPDFLoader(path)
        documents = loader.load()

        for doc in documents:
            doc.page_content = clean_text(doc.page_content)

        if self.config.use_parent_child:
            self.parent_chunks, child_chunks = self._build_parent_child(documents)
        else:
            child_chunks = self._build_flat_chunks(documents)

        self.child_chunks_flat = child_chunks
        self.db = self._get_or_create_db(child_chunks)

        if self.config.use_hybrid_search:
            self._build_bm25(child_chunks)

        print(f"Loaded '{path}' → {len(child_chunks)} chunks in DB.")

    def _build_flat_chunks(self, documents):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.parent_chunk_size,
            chunk_overlap=self.config.parent_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_documents(documents)

    def _build_parent_child(self, documents):
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.parent_chunk_size,
            chunk_overlap=self.config.parent_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.child_chunk_size,
            chunk_overlap=self.config.child_chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        parent_chunks = {}
        child_chunks = []

        for i, parent in enumerate(parent_splitter.split_documents(documents)):
            parent_id = f"parent_{i}"
            parent.metadata["parent_id"] = parent_id
            parent_chunks[parent_id] = parent

            for child in child_splitter.split_documents([parent]):
                child.metadata["parent_id"] = parent_id
                child_chunks.append(child)

        return parent_chunks, child_chunks

    #  Database 

    def _get_or_create_db(self, chunks):
        db_exists = (
            os.path.exists(self.config.persist_directory)
            and len(os.listdir(self.config.persist_directory)) > 0
        )
        if db_exists:
            print("Loading existing DB...")
            return Chroma(
                persist_directory=self.config.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.config.collection_name
            )
        print("Creating fresh DB...")
        return Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.config.persist_directory,
            collection_name=self.config.collection_name
        )

    #  BM25 

    def _build_bm25(self, chunks):
        tokenized = [c.page_content.lower().split() for c in chunks]
        self.bm25 = BM25Okapi(tokenized)
        print("BM25 index built.")

    #  Retrieval Strategies 

    def _vector_search(self, query: str):
        return self.db.similarity_search_with_score(
            query=query,
            k=self.config.retrieval_k,
            filter=self.config.metadata_filter
        )

    def _bm25_search(self, query: str):
        scores = self.bm25.get_scores(query.lower().split())
        results = sorted(
            zip(self.child_chunks_flat, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return results[:self.config.retrieval_k]

    def _hybrid_search(self, query: str):
        """RRF fusion of BM25 + vector results."""
        bm25_results = self._bm25_search(query)
        vector_results = self._vector_search(query)

        rrf_scores = defaultdict(float)
        doc_lookup = {}
        k = self.config.rrf_k

        for rank, (doc, _) in enumerate(bm25_results, start=1):
            key = doc.page_content
            doc_lookup[key] = doc
            rrf_scores[key] += 1 / (k + rank)

        for rank, (doc, _) in enumerate(vector_results, start=1):
            key = doc.page_content
            doc_lookup[key] = doc
            rrf_scores[key] += 1 / (k + rank)

        return [
            (doc_lookup[key], score)
            for key, score in sorted(
                rrf_scores.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _get_parent(self, child_doc: Document):
        """Swap a child chunk for its parent."""
        parent_id = child_doc.metadata.get("parent_id")
        if parent_id and parent_id in self.parent_chunks:
            return self.parent_chunks[parent_id]
        return child_doc   # fallback to child if no parent found

    def _retrieve(self, query: str):
        """Core retrieval: hybrid or vector → parent swap → rerank."""
        if self.config.use_hybrid_search and self.bm25:
            results = self._hybrid_search(query)
        else:
            results = self._vector_search(query)

        # Rerank
        pairs = [[query, doc.page_content] for doc, _ in results]
        scores = self.reranker.predict(pairs)
        reranked = sorted(
            [(results[i][0], float(scores[i])) for i in range(len(results))],
            key=lambda x: x[1],
            reverse=True
        )
        top = reranked[:self.config.top_n_rerank]

        # Parent swap
        if self.config.use_parent_child:
            seen = set()
            final = []
            for child, score in top:
                parent = self._get_parent(child)
                pid = parent.metadata.get("parent_id", child.page_content)
                if pid not in seen:
                    seen.add(pid)
                    final.append((parent, score))
            return final

        return top

    #  Query Expansion 

    def _multi_query(self, query: str):
        """Generate rephrased versions of the query."""
        response = chat(
            model=self.config.llm_model,
            messages=[{
                "role": "user",
                "content": f"""Rephrase this query into 3 different versions.
Return ONLY valid JSON, no explanation.

Query: {query}

{{"queries": ["...", "...", "..."]}}"""
            }]
        )
        raw = strip_think_tags(response["message"]["content"])
        try:
            return json.loads(raw)["queries"]
        except Exception:
            return []   # if parsing fails, fall back gracefully

    def _hyde(self, query: str):
        """Generate a hypothetical answer for better retrieval."""
        response = chat(
            model=self.config.llm_model,
            messages=[{
                "role": "user",
                "content": f"""Write a short factual paragraph that directly answers this question.
Write as if you found it in a document. No preamble.

Question: {query}
Answer:"""
            }]
        )
        return strip_think_tags(response["message"]["content"])

    # Compression 

    def _compress(self, query: str, docs):
        """Extract only query-relevant sentences from each chunk."""
        compressed = []
        for doc, score in docs:
            response = chat(
                model=self.config.llm_model,
                messages=[{
                    "role": "user",
                    "content": f"""Extract only sentences from the passage directly relevant to the question.
If nothing is relevant, reply with NOT RELEVANT. No explanation.

Question: {query}
Passage: {doc.page_content}
Extract:"""
                }]
            )
            extract = strip_think_tags(response["message"]["content"])
            if "NOT RELEVANT" not in extract and len(extract.strip()) > 20:
                compressed.append((doc, score, extract))
        return compressed

    # Main Query Entry Point

    def query(self, true_query: str, verbose: bool = True) -> str:
        """Run the full RAG pipeline and return the answer."""

        # Build all queries to retrieve with
        all_queries = [true_query]

        if self.config.use_multi_query:
            all_queries += self._multi_query(true_query)

        if self.config.use_hyde:
            all_queries.append(self._hyde(true_query))

        # Retrieve for each query, pool results
        seen = {}
        for q in all_queries:
            for doc, score in self._retrieve(q):
                key = doc.page_content
                if key not in seen:
                    seen[key] = (doc, score)

        unique_results = list(seen.values())

        # Final rerank against the TRUE query
        pairs = [[true_query, doc.page_content] for doc, _ in unique_results]
        scores = self.reranker.predict(pairs)
        reranked = sorted(
            [(unique_results[i][0], float(scores[i])) for i in range(len(unique_results))],
            key=lambda x: x[1],
            reverse=True
        )
        final = reranked[:self.config.top_n_rerank]

        # Compression (optional)
        if self.config.use_compression:
            compressed = self._compress(true_query, final)
            context = "\n\n".join(e for _, _, e in compressed)
        else:
            context = "\n\n".join(doc.page_content for doc, _ in final)

        if verbose:
            print("\n" + "="*20 + " Retrieved Context " + "="*20)
            for i, (doc, score) in enumerate(final, 1):
                print(f"[{i}] Page: {doc.metadata.get('page', '?')} | Score: {score:.4f}")
                print(f"     {doc.page_content[:100]}...")
            print("="*59)

        # Generate answer
        prompt = (
            f"Answer ONLY using the provided context. "
            f"If you don't know, say so.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{true_query}\n\nAnswer:"
        )
        stream = chat(
            model=self.config.llm_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        print("\nAI Answer: ", end="", flush=True)
        answer = ""
        for chunk in stream:
            token = chunk["message"]["content"]
            print(token, end="", flush=True)
            answer += token
        print()

        return answer