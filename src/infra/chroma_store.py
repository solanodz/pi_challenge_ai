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

    def _parse_hits(self, result: dict) -> list[RetrievalHit]:
        if not result["ids"] or not result["ids"][0]:
            return []
        hits: list[RetrievalHit] = []
        for idx, chunk_id in enumerate(result["ids"][0]):
            metadata = (result["metadatas"][0][idx] or {}) if result["metadatas"] else {}
            hits.append(
                RetrievalHit(
                    chunk_id=chunk_id,
                    document=result["documents"][0][idx],
                    section_title=metadata.get("section_title", ""),
                    distance=float(result["distances"][0][idx]),
                )
            )
        return hits

    def query_top1(self, embedding: list[float]) -> RetrievalHit | None:
        hits = self.query_top_k(embedding, n_results=1)
        return hits[0] if hits else None

    def query_top_k(self, embedding: list[float], n_results: int = 1) -> list[RetrievalHit]:
        if self.count() == 0:
            return []
        n_results = min(n_results, self.count())
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        return self._parse_hits(result)

    def count(self) -> int:
        return self._collection.count()
