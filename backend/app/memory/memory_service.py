from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import models, repositories
import re

class MemoryService:
    """Manages short-term and long-term user context, recurring patterns, and excuses."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = repositories.MemoryRepository(db)

    def record_interaction_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        tags: List[str] = None,
        importance_score: float = 0.8
    ) -> models.MemoryRecord:
        """Stores an extracted behavioral pattern, commitment style, or excuse observation."""
        tag_str = ",".join(tags) if tags else ""
        return self.repo.add(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            tags=tag_str,
            importance_score=importance_score
        )

    def get_user_context(self, user_id: str, query_hint: Optional[str] = None, limit: int = 5) -> str:
        """
        Retrieves formatted memory context for an agent prompt.
        Matches against query_hint or returns the highest priority recent observations.
        """
        records = self.repo.get_recent(user_id=user_id, limit=limit * 2)
        if not records:
            return "No previous behavioral history recorded yet. Fresh slate."

        # If query_hint is provided, rank by keyword overlap
        if query_hint:
            words = set(re.findall(r"\w+", query_hint.lower()))
            def score(rec: models.MemoryRecord):
                rec_words = set(re.findall(r"\w+", (rec.content + " " + rec.tags).lower()))
                overlap = len(words.intersection(rec_words))
                return overlap * rec.importance_score

            records = sorted(records, key=score, reverse=True)

        selected = records[:limit]
        lines = []
        for r in selected:
            lines.append(f"- [{r.memory_type}]: {r.content}")
        return "\n".join(lines)

    def detect_and_store_excuses(self, user_id: str, task_title: str, user_response: str) -> Optional[models.MemoryRecord]:
        """Detects recurring excuse patterns and logs them to memory."""
        lower = user_response.lower()
        excuse_triggers = [
            ("fatigue", ["tired", "exhausted", "sleepy", "no energy", "burnout"]),
            ("time_management", ["busy", "no time", "later", "tomorrow", "distracted", "forgot"]),
            ("external_blame", ["work made me", "boss called", "traffic", "wifi down", "weather"]),
            ("procrastination", ["didnt feel like it", "not in the mood", "scrolled", "gaming"])
        ]

        detected_tag = None
        for category, triggers in excuse_triggers:
            if any(t in lower for t in triggers):
                detected_tag = category
                break

        if detected_tag:
            content = f"User gave excuse regarding task '{task_title}': '{user_response}'. Pattern identified: {detected_tag}."
            return self.record_interaction_memory(
                user_id=user_id,
                memory_type="EXCUSE_PATTERN",
                content=content,
                tags=[detected_tag, "avoidance"],
                importance_score=0.9
            )
        return None
