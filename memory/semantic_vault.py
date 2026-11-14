import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from config.settings import DATABASE_PATH

class EkhtizalyMemoryVault:
    """
    Ekhtizaly Autonomous Core - High-Performance Local Semantic Vault.
    Provides local full-text search (BM25 via FTS5), mission telemetry logs,
    lead storage, and audit history with zero external cloud dependencies.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Structured Knowledge Documents
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_vault (
                doc_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata_json TEXT,
                created_at REAL
            );
            """)

            # 2. FTS5 Index for Fast BM25 Local Information Retrieval
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                doc_id UNINDEXED,
                title,
                content,
                tokenize='unicode61'
            );
            """)

            # 3. Mission Execution Journal
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mission_vault (
                mission_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                params_json TEXT,
                steps_json TEXT,
                result_json TEXT,
                started_at REAL,
                completed_at REAL
            );
            """)

            # 4. Intelligence & Lead Harvesting Vault
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_vault (
                lead_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT,
                url TEXT,
                extracted_data_json TEXT,
                score REAL DEFAULT 0.0,
                created_at REAL
            );
            """)

            # 5. Operational Telemetry & Latency Metrics
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trace_id TEXT NOT NULL,
                component TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                details_json TEXT,
                created_at REAL
            );
            """)

            conn.commit()

    def store_document(self, doc_id: str, title: str, content: str, category: str = "general", metadata: Optional[Dict[str, Any]] = None) -> bool:
        meta_str = json.dumps(metadata or {})
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO knowledge_vault (doc_id, category, title, content, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (doc_id, category, title, content, meta_str, now)
            )
            # Update FTS
            cursor.execute("DELETE FROM knowledge_fts WHERE doc_id = ?", (doc_id,))
            cursor.execute(
                """
                INSERT INTO knowledge_fts (doc_id, title, content)
                VALUES (?, ?, ?)
                """,
                (doc_id, title, content)
            )
            conn.commit()
            return True

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches indexed documents using BM25 relevance scoring via SQLite FTS5."""
        sanitized_query = "".join([c for c in query if c.isalnum() or c.isspace()]).strip()
        if not sanitized_query:
            return []

        # Convert to prefix query for natural search
        tokens = sanitized_query.split()
        fts_query = " ".join([f'"{tok}"*' for tok in tokens])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT f.doc_id, f.title, f.content, bm25(knowledge_fts) as rank,
                           k.category, k.metadata_json, k.created_at
                    FROM knowledge_fts f
                    JOIN knowledge_vault k ON f.doc_id = k.doc_id
                    WHERE knowledge_fts MATCH ?
                    ORDER BY rank ASC
                    LIMIT ?
                    """,
                    (fts_query, limit)
                )
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "doc_id": row["doc_id"],
                        "category": row["category"],
                        "title": row["title"],
                        "content": row["content"],
                        "relevance_rank": round(float(row["rank"]), 4),
                        "metadata": json.loads(row["metadata_json"] or "{}"),
                        "created_at": row["created_at"]
                    })
                return results
            except Exception:
                # Fallback to LIKE query if FTS syntax fails
                cursor.execute(
                    """
                    SELECT doc_id, category, title, content, metadata_json, created_at
                    FROM knowledge_vault
                    WHERE title LIKE ? OR content LIKE ?
                    LIMIT ?
                    """,
                    (f"%{sanitized_query}%", f"%{sanitized_query}%", limit)
                )
                rows = cursor.fetchall()
                return [{
                    "doc_id": r["doc_id"],
                    "category": r["category"],
                    "title": r["title"],
                    "content": r["content"],
                    "relevance_rank": 0.0,
                    "metadata": json.loads(r["metadata_json"] or "{}"),
                    "created_at": r["created_at"]
                } for r in rows]

    def record_mission_start(self, mission_id: str, title: str, params: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO mission_vault (mission_id, title, status, params_json, steps_json, result_json, started_at)
                VALUES (?, ?, 'RUNNING', ?, '[]', '{}', ?)
                """,
                (mission_id, title, json.dumps(params), time.time())
            )
            conn.commit()
            return True

    def record_mission_completion(self, mission_id: str, status: str, steps: List[Dict[str, Any]], result: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE mission_vault
                SET status = ?, steps_json = ?, result_json = ?, completed_at = ?
                WHERE mission_id = ?
                """,
                (status, json.dumps(steps), json.dumps(result), time.time(), mission_id)
            )
            conn.commit()
            return True

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mission_vault WHERE mission_id = ?", (mission_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "mission_id": row["mission_id"],
                "title": row["title"],
                "status": row["status"],
                "params": json.loads(row["params_json"] or "{}"),
                "steps": json.loads(row["steps_json"] or "[]"),
                "result": json.loads(row["result_json"] or "{}"),
                "started_at": row["started_at"],
                "completed_at": row["completed_at"]
            }

    def store_lead(self, lead_id: str, source: str, title: str, url: str, data: Dict[str, Any], score: float = 0.0) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO intelligence_vault (lead_id, source, title, url, extracted_data_json, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (lead_id, source, title, url, json.dumps(data), score, time.time())
            )
            conn.commit()
            return True

    def list_leads(self, source: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if source:
                cursor.execute("SELECT * FROM intelligence_vault WHERE source = ? ORDER BY score DESC, created_at DESC LIMIT ?", (source, limit))
            else:
                cursor.execute("SELECT * FROM intelligence_vault ORDER BY score DESC, created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [{
                "lead_id": r["lead_id"],
                "source": r["source"],
                "title": r["title"],
                "url": r["url"],
                "data": json.loads(r["extracted_data_json"] or "{}"),
                "score": r["score"],
                "created_at": r["created_at"]
            } for r in rows]

    def log_telemetry(self, trace_id: str, component: str, operation: str, status: str, latency_ms: float, details: Optional[Dict[str, Any]] = None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO telemetry_logs (trace_id, component, operation, status, latency_ms, details_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (trace_id, component, operation, status, latency_ms, json.dumps(details or {}), time.time())
            )
            conn.commit()

vault = EkhtizalyMemoryVault()
