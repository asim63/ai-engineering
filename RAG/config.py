from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RAGConfig:
    #Chunking
    parent_chunk_size: int = 800
    parent_chunk_overlap: int = 100
    child_chunk_size: int = 200
    child_chunk_overlap: int = 20
    
    #Retrieval
    retrieval_k: int = 10
    top_n_rerank: int = 3
    rrf_k: int = 60
    
    #Models
    llm_model: str = "qwen3:8b"
    embedding_model: str ="all-MiniLM-L6-v2"
    reranker_model: str = "BAAI/bge-reranker-base"
    
    #Strategy toggles
    use_hyde: bool = True
    use_multi_query: bool = True
    use_parent_child: bool = True
    use_hybrid_search: bool = True
    use_compression: bool = False
    
    metadata_filter: Optional[dict] = None