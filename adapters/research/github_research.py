"""Optional, bounded GitHub code-search adapter for the advanced research exercise."""

import json
from datetime import datetime, timezone
from urllib import error, parse, request


class GitHubResearch:
    """Search public GitHub code and return small, citable evidence records."""

    def __init__(self, token, max_requests=3, max_results=3):
        """Store a GitHub token and small budgets for one repair session."""
        self.token = token
        self.max_requests = max_requests
        self.max_results = max_results
        self.requests_used = 0

    def search_code(self, query):
        """Search GitHub code and return linked evidence without exposing the token."""
        if not isinstance(query, str) or not query.strip() or "\n" in query or len(query) > 180:
            return {"ok": False, "output": "Research queries must be one line and at most 180 characters.", "sources": []}
        if self.requests_used >= self.max_requests:
            return {"ok": False, "output": "GitHub research request budget exhausted.", "sources": []}

        self.requests_used += 1
        url = "https://api.github.com/search/code?" + parse.urlencode({"q": query, "per_page": self.max_results})
        api_request = request.Request(url, headers={
            "Accept": "application/vnd.github.text-match+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "coding-agent-lab",
            "X-GitHub-Api-Version": "2026-03-10",
        })
        try:
            with request.urlopen(api_request, timeout=10) as response:
                payload = json.loads(response.read())
        except error.HTTPError as problem:
            return {"ok": False, "output": f"GitHub search failed with HTTP {problem.code}.", "sources": []}
        except error.URLError as problem:
            return {"ok": False, "output": f"GitHub search is unavailable: {problem.reason}", "sources": []}

        sources = []
        for item in payload.get("items", [])[:self.max_results]:
            matches = item.get("text_matches") or []
            snippet = matches[0].get("fragment", "")[:500] if matches else ""
            sources.append({
                "url": item.get("html_url", ""),
                "repository": item.get("repository", {}).get("full_name", ""),
                "path": item.get("path", ""),
                "snippet": snippet,
            })
        return {
            "ok": True,
            "query": query,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "incomplete": bool(payload.get("incomplete_results")),
            "sources": sources,
        }
