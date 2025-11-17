from pathlib import Path
from typing import Dict, List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from fastapi import HTTPException

from config import Settings
from schemas import DocumentChunk


class RAGService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.openai_api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY no configurada")
        self.embedding = OpenAIEmbeddings(model=self.settings.embedding_model, api_key=self.settings.openai_api_key)
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=self.settings.temperature,
            api_key=self.settings.openai_api_key,
        )
        self.vectorstores: Dict[str, Chroma] = {}

    def list_clients(self) -> List[str]:
        return ["ACME", "CAME"]

    def _client_pdf_path(self, client: str) -> Path:
        pdf_name = f"{client.upper()}_procedimiento.pdf"
        pdf_path = Path(self.settings.docs_path) / pdf_name
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"Documento no encontrado para el cliente {client}")
        return pdf_path

    def _load_documents(self, client: str) -> List[Document]:
        pdf_path = self._client_pdf_path(client)
        loader = PyPDFLoader(str(pdf_path))
        return loader.load()

    def _build_vectorstore(self, client: str) -> Chroma:
        documents = self._load_documents(client)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size, chunk_overlap=self.settings.chunk_overlap
        )
        chunks = splitter.split_documents(documents)
        persist_dir = Path(self.settings.chroma_dir) / client.lower()
        persist_dir.mkdir(parents=True, exist_ok=True)
        collection_name = f"{client.lower()}_collection"
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embedding,
            collection_name=collection_name,
            persist_directory=str(persist_dir),
        )
        vectorstore.persist()
        self.vectorstores[client.upper()] = vectorstore
        return vectorstore

    def _get_vectorstore(self, client: str) -> Chroma:
        client_key = client.upper()
        if client_key in self.vectorstores:
            return self.vectorstores[client_key]
        persist_dir = Path(self.settings.chroma_dir) / client_key.lower()
        collection_name = f"{client_key.lower()}_collection"
        if persist_dir.exists() and any(persist_dir.iterdir()):
            vectorstore = Chroma(
                embedding_function=self.embedding,
                collection_name=collection_name,
                persist_directory=str(persist_dir),
            )
            self.vectorstores[client_key] = vectorstore
            return vectorstore
        return self._build_vectorstore(client_key)

    def query(self, client: str, question: str) -> tuple[str, List[DocumentChunk]]:
        client_key = client.upper()
        if client_key not in self.list_clients():
            raise HTTPException(status_code=400, detail="Cliente no soportado")
        if not question.strip():
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía")

        vectorstore = self._get_vectorstore(client_key)
        retriever = vectorstore.as_retriever(search_kwargs={"k": self.settings.k_results})
        relevant_docs: List[Document] = retriever.invoke(question)

        context_blocks = []
        chunk_responses: List[DocumentChunk] = []
        for doc in relevant_docs:
            source = Path(doc.metadata.get("source", "")).name
            page = doc.metadata.get("page", "?")
            context_blocks.append(f"Fuente: {source} (página {page})\n{doc.page_content}")
            chunk_responses.append(DocumentChunk(text=doc.page_content, source=source, page=page))

        context_text = "\n\n".join(context_blocks)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Eres un asistente experto en operaciones de un Centro de Operaciones de Monitoreo (COM). "
                    "Responde con precisión usando exclusivamente el contexto proporcionado. "
                    "Si la información no está en el contexto, indica que no está disponible. "
                    "Responde en el mismo idioma de la pregunta.",
                ),
                (
                    "human",
                    "Contexto:\n{context}\n\nPregunta: {question}\nRespuesta:",
                ),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke({"context": context_text, "question": question})
        answer = response.content if hasattr(response, "content") else str(response)
        return answer, chunk_responses
