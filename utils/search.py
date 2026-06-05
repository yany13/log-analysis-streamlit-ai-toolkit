"""Search utilities."""
from langchain_community.tools import DuckDuckGoSearchRun


def web_search(query):
    """
    Search the web using DuckDuckGo.

    Args:
        query: Search query

    Returns:
        Search results or error message
    """
    try:
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Web search skipped: {str(e)}"
