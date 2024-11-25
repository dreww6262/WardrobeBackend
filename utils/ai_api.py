"""Utility module for RAG operations using Claude and ChromaDB."""
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass

from anthropic import Anthropic
from chromadb import PersistentClient
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.language_models import BaseChatModel


@dataclass
class RAGResponse:
    """Structured response from RAG queries."""

    answer: Optional[str]
    sources: Optional[List[str]]
    error: Optional[str]


class ClaudeLLMHelper:
    """Helper class for RAG operations using Claude and ChromaDB."""

    def __init__(self, model_name: str = "claude-3-sonnet-20240229") -> None:
        """Initialize the Claude helper with API keys and models.

        Args:
            model_name: The Claude model to use. Defaults to claude-3-sonnet.

        Raises:
            ValueError: If required API keys are not found in environment.
        """
        load_dotenv()

        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

        if not self.anthropic_api_key:
            raise ValueError(
                "Anthropic API key not found in environment variables"
            )
        if not self.huggingface_api_key:
            raise ValueError(
                "HuggingFace API key not found in environment variables"
            )

        # Direct Anthropic client for custom calls
        self.client = Anthropic(api_key=self.anthropic_api_key)

        # LangChain integration for RAG
        self.llm: BaseChatModel = ChatAnthropic(
            model=model_name,
            anthropic_api_key=self.anthropic_api_key,
            temperature=0.7,
        )

        # Using HuggingFace Hub for embeddings - no local models required
        self.embeddings = HuggingFaceHubEmbeddings(
            huggingface_api_token=self.huggingface_api_key,
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            task="feature-extraction",
        )

        self.vector_store: Optional[VectorStore] = None
        self.qa_chain: Optional[RetrievalQA] = None

    def create_vector_store(
        self,
        documents: List[str],
        collection_name: str = "default_collection",
        persist_directory: str = "./chroma_db",
    ) -> bool:
        """Create a vector store from a list of documents.

        Args:
            documents: List of text documents to store.
            collection_name: Name for the ChromaDB collection.
            persist_directory: Directory to store the vector database.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            client = PersistentClient(path=persist_directory)

            self.vector_store = Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )

            self.vector_store.add_texts(documents)
            return True

        except Exception as exc:
            print(f"Error creating vector store: {str(exc)}")
            return False

    def load_vector_store(
        self,
        collection_name: str = "default_collection",
        persist_directory: str = "./chroma_db",
    ) -> bool:
        """Load a persisted vector store.

        Args:
            collection_name: Name of the ChromaDB collection to load.
            persist_directory: Directory where the vector database is stored.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            client = PersistentClient(path=persist_directory)

            self.vector_store = Chroma(
                client=client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
            return True
        except Exception as exc:
            print(f"Error loading vector store: {str(exc)}")
            return False

    def setup_qa_chain(self, custom_prompt: Optional[str] = None) -> None:
        """Set up the QA chain with the vector store.

        Args:
            custom_prompt: Optional custom prompt template.

        Raises:
            ValueError: If vector store is not initialized.
        """
        if not self.vector_store:
            raise ValueError(
                "Vector store not initialized. "
                "Please create or load one first."
            )

        default_prompt = (
            "Use the following pieces of context to answer the question.\n"
            "If you don't know the answer, just say you don't know.\n\n"
            "Context: {context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )

        prompt = PromptTemplate(
            template=custom_prompt or default_prompt,
            input_variables=["context", "question"],
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}  # Number of relevant chunks to return
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

    async def query(self, question: str) -> RAGResponse:
        """Query Claude with RAG context using LangChain.

        Args:
            question: The question to ask.

        Returns:
            RAGResponse: Contains answer, sources, and any error messages.
        """
        if not self.qa_chain:
            return RAGResponse(
                answer=None,
                sources=None,
                error=(
                    "QA chain not initialized. "
                    "Please run setup_qa_chain first."
                ),
            )

        try:
            response = await self.qa_chain.ainvoke({"query": question})
            return RAGResponse(
                answer=response["result"],
                sources=[
                    doc.page_content for doc in response["source_documents"]
                ],
                error=None,
            )
        except Exception as exc:
            return RAGResponse(
                answer=None,
                sources=None,
                error=str(exc),
            )

    async def direct_query(
        self, system_prompt: str, user_message: str
    ) -> Dict[str, Any]:
        """Make a direct query to Claude without RAG context.

        Args:
            system_prompt: The system prompt for Claude.
            user_message: The user's message/query.

        Returns:
            Dict containing either the response or error message.
        """
        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return {"content": message.content, "error": None}
        except Exception as exc:
            return {"content": None, "error": str(exc)}


# Example Django view
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
async def rag_query(request):
    try:
        data = json.loads(request.body)
        question = data.get("question")

        if not question:
            return JsonResponse({"error": "No question provided"}, status=400)

        llm_helper = ClaudeLLMHelper()
        llm_helper.load_vector_store()
        llm_helper.setup_qa_chain()

        response = await llm_helper.query(question)
        return JsonResponse(response.__dict__)

    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
"""
