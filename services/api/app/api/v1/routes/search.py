from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    TraceDetailResponse,
    TraceListResponse,
)
from app.search import service as search_service
from app.search.dense_retriever import (
    DenseRetrievalError,
    InvalidDenseSearchRequestError,
    NoVectorIndexError,
)
from app.search.hybrid_retriever import HybridRetrievalError, InvalidHybridSearchRequestError
from app.search.lexical_retriever import InvalidSearchRequestError, NoActiveIndexError, RetrievalError
from app.search.reranker import InvalidRerankSearchRequestError, RerankSearchError

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    search_request: SearchRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> SearchResponse:
    try:
        return search_service.run_search(
            db,
            search_request,
            request_id=getattr(request.state, "request_id", None),
        )
    except (NoActiveIndexError, NoVectorIndexError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (
        InvalidSearchRequestError,
        InvalidDenseSearchRequestError,
        InvalidHybridSearchRequestError,
        InvalidRerankSearchRequestError,
        RetrievalError,
        DenseRetrievalError,
        HybridRetrievalError,
        RerankSearchError,
        ValueError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/traces", response_model=TraceListResponse)
async def list_search_traces(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> TraceListResponse:
    return search_service.list_query_traces(db, limit=limit, offset=offset)


@router.get("/traces/{trace_id}", response_model=TraceDetailResponse)
async def search_trace_detail(
    trace_id: UUID,
    db: Session = Depends(get_db),
) -> TraceDetailResponse:
    detail = search_service.get_query_trace_detail(db, trace_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Search trace not found: {trace_id}",
        )
    return detail
