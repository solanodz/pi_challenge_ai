from dataclasses import dataclass

from chromadb.api.models.Collection import Collection


@dataclass
class RetrievalHit:
    chunk_id: str
    document: str
    section_title: str
    distance: float


class ChromaStore:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query_top1(self, embedding: list[float]) -> RetrievalHit | None:
        if self.count() == 0:
            return None
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=1,
            include=["documents", "metadatas", "distances"],
        )
        if not result["ids"] or not result["ids"][0]:
            return None
        metadata = result["metadatas"][0][0] or {}
        return RetrievalHit(
            chunk_id=result["ids"][0][0],
            document=result["documents"][0][0],
            section_title=metadata.get("section_title", ""),
            distance=float(result["distances"][0][0]),
        )

    def count(self) -> int:
        return self._collection.count()
