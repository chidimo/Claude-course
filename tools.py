tools = [
    {
        "name": "calculator",
        "description": "A tool to perform mathematical calculations.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "web_search",
        "description": "A tool to find information on the web.",
        "input_schema": {
            "type": "object",
            "properties": {"search_term": {"type": "string"}},
            "required": ["search_term"],
        },
    },
]
