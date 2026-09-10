TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate the browser to a specific URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to navigate to."}
            },
            "required": ["url"]
        }
    },
    {
        "name": "click",
        "description": "Click an element on the page, identified by a CSS selector or visible text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector or text to identify the element."}
            },
            "required": ["selector"]
        }
    },
    {
        "name": "type_text",
        "description": "Type text into an input field identified by a CSS selector.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of the input field."},
                "text": {"type": "string", "description": "The text to type."}
            },
            "required": ["selector", "text"]
        }
    },
    {
        "name": "screenshot",
        "description": "Take a screenshot of the current page state, for evidence.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
    "name": "finish_test",
    "description": "Call this when the test is complete, to report the final result.",
    "input_schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "enum": ["PASS", "FAIL", "BLOCKED"],
                "description": "PASS if the app behaved correctly. FAIL if the app has a genuine defect. BLOCKED if the test's precondition wasn't met and the app's correctness couldn't be evaluated."
            },
            "reason": {"type": "string", "description": "Brief explanation of the result."}
        },
        "required": ["result", "reason"]
    }
},
{
    "name": "select_dropdown_option",
    "description": "Select an option from a native HTML <select> dropdown by its visible text label. Use this instead of click for <select> elements — clicking does not work reliably on native dropdowns.",
    "input_schema": {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector of the <select> element."},
            "label": {"type": "string", "description": "The visible text of the option to select, e.g. 'IT'."}
        },
        "required": ["selector", "label"]
    }
},
{
    "name": "read_page",
    "description": "Get a list of interactive elements currently visible on the page, with their data-testid attributes. Call this before clicking or typing, to find the correct selector rather than guessing.",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
},
{
    "name": "query_database",
    "description": "Run a read-only SELECT query directly against the database to verify data actually changed. Use this after any action that should have created, updated, or deleted data — do not rely on the UI alone for verification.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "A SELECT SQL query to run against the HrManagement database."}
        },
        "required": ["query"]
    }
}
]
