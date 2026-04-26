from __future__ import annotations

import argparse
import json
import math
import sys

from app.core.config import get_settings
from app.ml.embeddings import embed_text, get_embedding_dimension


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed text with the local embedding model.")
    parser.add_argument("text")
    parser.add_argument("--model")
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--show-vector", action="store_true")
    parser.add_argument("--preview-dimensions", type=int, default=8)
    return parser.parse_args()


def _preview_text(text: str, limit: int = 120) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else f"{compact[: limit - 3]}..."


def main() -> int:
    args = parse_args()
    try:
        settings = get_settings()
        normalize = not args.no_normalize
        vector = embed_text(args.text, model_name=args.model, normalize=normalize)
        dimension = get_embedding_dimension(args.model)
        preview_dimensions = max(args.preview_dimensions, 0)
        payload = {
            "model_name": args.model or settings.EMBEDDING_MODEL,
            "dimension": dimension or len(vector),
            "vector_preview": vector[:preview_dimensions],
            "vector_norm": math.sqrt(sum(value * value for value in vector)),
            "text_preview": _preview_text(args.text),
            "normalized": normalize,
        }
        if args.show_vector:
            payload["vector"] = vector
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
