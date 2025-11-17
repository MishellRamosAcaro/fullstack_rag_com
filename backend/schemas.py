from typing import List

from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    client: str = Field(..., description="Nombre del cliente a consultar")
    question: str = Field(..., description="Pregunta del operador")


class DocumentChunk(BaseModel):
    text: str
    source: str
    page: int | str


class RagQueryResponse(BaseModel):
    answer: str
    chunks: List[DocumentChunk]
