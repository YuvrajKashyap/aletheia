from __future__ import annotations


def build_lexical_index_body() -> dict:
    return {
        "mappings": {
            "properties": {
                "chunk_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "dataset_id": {"type": "keyword"},
                "document_external_id": {"type": "keyword"},
                "chunk_external_id": {"type": "keyword"},
                "chunk_index": {"type": "integer"},
                "title": {"type": "text"},
                "text": {"type": "text"},
                "token_count": {"type": "integer"},
                "content_hash": {"type": "keyword"},
                "chunking_strategy": {"type": "keyword"},
                "chunking_version": {"type": "keyword"},
                "metadata_json": {"type": "object", "enabled": True},
                "created_at": {"type": "date"},
            }
        }
    }
