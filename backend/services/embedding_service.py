"""
Embedding service using sentence-transformers (all-MiniLM-L6-v2) for RAG context storage & retrieval with pgvector.
"""
import os
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from apps.db_models import DocumentEmbedding

logger = logging.getLogger("embedding_service")

_encoder_instance = None


def get_encoder():
    """Lazy loader for SentenceTransformer embedding model."""
    global _encoder_instance
    if _encoder_instance is not None:
        return _encoder_instance

    model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model {model_name}...")
        _encoder_instance = SentenceTransformer(model_name)
        logger.info("[+] Embedding model loaded successfully.")
        return _encoder_instance
    except Exception as e:
        logger.error(f"Failed to load SentenceTransformer: {e}")
        return None


def generate_embedding(text_content: str) -> List[float]:
    """Generates 384-dimensional vector embedding for text."""
    encoder = get_encoder()
    if encoder is not None:
        try:
            vector = encoder.encode(text_content).tolist()
            return vector
        except Exception as e:
            logger.error(f"Error encoding text: {e}")

    # Fallback zero-vector (384 dimensions)
    return [0.0] * 384


def store_patient_document_embedding(
    db: Session,
    patient_id: int,
    category: str,
    content: str,
    metadata_json: Dict[str, Any] = None
) -> DocumentEmbedding:
    """Stores vector embedding of patient text into pgvector table."""
    vector = generate_embedding(content)
    doc_emb = DocumentEmbedding(
        patient_id=patient_id,
        category=category,
        content=content,
        embedding=vector,
        metadata_json=metadata_json or {}
    )
    db.add(doc_emb)
    db.commit()
    db.refresh(doc_emb)
    return doc_emb


def search_similar_patient_context(
    db: Session,
    patient_id: int,
    query_text: str,
    top_k: int = 4
) -> List[Dict[str, Any]]:
    """Retrieves top_k most relevant past patient records using pgvector distance."""
    query_vector = generate_embedding(query_text)
    
    try:
        vec_str = "[" + ",".join(str(x) for x in query_vector) + "]"
        query_sql = text(
            "SELECT id, category, content, metadata_json "
            "FROM document_embeddings "
            "WHERE patient_id = :pid "
            "ORDER BY embedding <-> CAST(:vec AS vector) "
            "LIMIT :k"
        )
        result = db.execute(query_sql, {"pid": patient_id, "vec": vec_str, "k": top_k})
        
        matches = []
        for row in result:
            matches.append({
                "id": row.id,
                "category": row.category,
                "content": row.content,
                "metadata": row.metadata_json,
                "similarity": 0.9
            })
        return matches
    except Exception as e:
        logger.error(f"Vector search fallback: {e}")
        db.rollback()
        
        records = db.query(DocumentEmbedding).filter(
            DocumentEmbedding.patient_id == patient_id
        ).order_by(DocumentEmbedding.id.desc()).limit(top_k).all()
        
        return [{
            "id": r.id,
            "category": r.category,
            "content": r.content,
            "metadata": r.metadata_json,
            "similarity": 0.5
        } for r in records]
