import os

from app.services.function_calling import FunctionCaller, Tool, ToolRegistry
from app.services.web_search_service import WebSearchService

web_search_service = WebSearchService()
registry = ToolRegistry()
registry.register(
    Tool(
        name="web_search",
        description="Search the web and return structured summaries",
        args_schema={
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "count": {"type": "integer", "minimum": 1, "maximum": 10},
            },
        },
        handler=web_search_service.search,
    )
)
function_caller = FunctionCaller(registry=registry, max_retries=int(os.getenv("TOOL_MAX_RETRIES", "1")))
