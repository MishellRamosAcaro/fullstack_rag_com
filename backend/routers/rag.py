from fastapi import APIRouter, Depends, HTTPException

from config import get_settings
from schemas import RagQueryRequest, RagQueryResponse
from services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["rag"])


def get_rag_service() -> RAGService:
    settings = get_settings()
    return RAGService(settings)


@router.post("/query", response_model=RagQueryResponse)
def query_rag(request: RagQueryRequest, service: RAGService = Depends(get_rag_service)) -> RagQueryResponse:
    try:
        answer, chunks = service.query(request.client, request.question)
        return RagQueryResponse(answer=answer, chunks=chunks)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive against unexpected errors
        raise HTTPException(status_code=500, detail=str(exc)) from exc
