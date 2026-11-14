from fastmcp import FastMCP
from typing import Dict, Any
from engines.intelligence_radar import intelligence_radar

mcp = FastMCP("Ekhtizaly-Intelligence-Server")

@mcp.tool()
async def search_github_repositories(query: str, limit: int = 10) -> Dict[str, Any]:
    """Searches top open-source repositories by keyword, stars, and engagement metrics."""
    return intelligence_radar.search_github_repositories(query=query, limit=limit)

@mcp.tool()
async def search_discussions_and_issues(repo: str, query: str, limit: int = 10) -> Dict[str, Any]:
    """Analyzes community discussions, questions, and issues in a target repository."""
    return intelligence_radar.search_discussions_and_issues(repo=repo, query=query, limit=limit)

@mcp.tool()
async def analyze_topic_momentum(topic: str) -> Dict[str, Any]:
    """Calculates engagement velocity and demand score for a technological topic."""
    res = intelligence_radar.search_github_repositories(query=topic, limit=5)
    if res.get("status") != "SUCCESS":
        return res
    
    total_stars = sum([item.get("stars", 0) for item in res.get("items", [])])
    total_forks = sum([item.get("forks", 0) for item in res.get("items", [])])
    
    return {
        "status": "SUCCESS",
        "topic": topic,
        "sample_size": len(res.get("items", [])),
        "aggregate_stars": total_stars,
        "aggregate_forks": total_forks,
        "momentum_index": round((total_stars * 1.5 + total_forks * 3.0) / 1000.0, 2),
        "top_repositories": [item.get("name") for item in res.get("items", [])]
    }

server = mcp
