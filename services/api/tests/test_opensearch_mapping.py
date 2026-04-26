from app.search.lexical_mapping import build_lexical_index_body


def test_lexical_index_mapping_contains_expected_chunk_fields() -> None:
    body = build_lexical_index_body()
    properties = body["mappings"]["properties"]

    assert properties["text"]["type"] == "text"
    assert properties["title"]["type"] == "text"
    assert properties["chunk_id"]["type"] == "keyword"
    assert properties["document_id"]["type"] == "keyword"
    assert properties["dataset_id"]["type"] == "keyword"
    assert properties["content_hash"]["type"] == "keyword"
    assert properties["chunk_index"]["type"] == "integer"


def test_lexical_index_mapping_uses_default_bm25_without_custom_analyzers() -> None:
    body = build_lexical_index_body()

    assert "settings" not in body
    assert "analyzer" not in body["mappings"]["properties"]["text"]
