import logging
import chromadb
from chromadb.config import Settings
from backend.app.config.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            # Persistent Client
            self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            
            # Get or Create Collection
            self.collection = self.client.get_or_create_collection(name="market_news")
            logger.info(f"Connected to ChromaDB at {settings.VECTOR_DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")

    def add_documents(self, documents: list, metadatas: list, ids: list):
        if self.collection:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to Vector DB")

    def query(self, query_text: str, n_results: int = 5):
        if self.collection:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        return None

vector_store = VectorStore()
