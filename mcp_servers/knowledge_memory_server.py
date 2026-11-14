from fastmcp import FastMCP
from typing import Dict, Any, List
import uuid
from memory.semantic_vault import vault

mcp = FastMCP("Ekhtizaly-Knowledge-Memory-Server")

@mcp.tool()
async def vault_store_knowledge(title: str, content: str, category: str = "general") -> Dict[str, Any]:
    """Persists structured knowledge or intelligence notes into the local FTS5 semantic vault."""
    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    success = vault.store_document(doc_id=doc_id, title=title, content=content, category=category)
    return {
        "status": "STORED" if success else "FAILED",
        "doc_id": doc_id,
        "title": title,
        "category": category
    }

@mcp.tool()
async def vault_search_knowledge(query: str, limit: int = 5) -> Dict[str, Any]:
    """Retrieves relevant indexed documents using BM25 relevance ranking."""
    matches = vault.search_documents(query=query, limit=limit)
    return {
        "status": "SUCCESS",
        "query": query,
        "matches_count": len(matches),
        "documents": matches
    }

@mcp.tool()
async def vault_list_harvested_leads(source: str = "", limit: int = 20) -> Dict[str, Any]:
    """Lists prioritized commercial leads extracted during autonomous reconnaissance."""
    leads = vault.list_leads(source=source if source else None, limit=limit)
    return {
        "status": "SUCCESS",
        "leads_count": len(leads),
        "leads": leads
    }

server = mcp
