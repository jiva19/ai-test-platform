import pymssql
import os
import json
import datetime
from repositories.results_repository import complete_run
from prompts import build_prompt
from models import TestCase
from dotenv import load_dotenv
from anthropic import Anthropic
from playwright.sync_api import sync_playwright
from tools import TOOLS

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))



def execute_tool(page, tool_name, tool_input, screenshot_dir):
    if tool_name == "navigate":
        page.goto(tool_input["url"])
        return "Navigated successfully."
    elif tool_name == "click":
        page.click(tool_input["selector"])
        return "Clicked successfully."
    elif tool_name == "type_text":
        page.fill(tool_input["selector"], tool_input["text"])
        return "Typed successfully."
    elif tool_name == "screenshot":
        filename = f"step_{datetime.datetime.now().strftime('%H%M%S_%f')}.png"
        path = os.path.join(screenshot_dir, filename)
        page.screenshot(path=path)
        return f"Screenshot saved to {path}."
    elif tool_name == "select_dropdown_option":
        page.select_option(tool_input["selector"], label=tool_input["label"])
        return "Option selected successfully."
    elif tool_name == "read_page":
        elements = page.eval_on_selector_all(
            "[data-testid]",
            "els => els.map(el => ({ testid: el.getAttribute('data-testid'), tag: el.tagName, text: el.innerText }))"
        )
        return json.dumps(elements)
    elif tool_name == "query_database":
        query = tool_input["query"].strip()
        if not query.upper().startswith("SELECT"):
            return "Error: only SELECT queries are allowed for verification."
        try:
          conn = pymssql.connect(
            server="localhost",
            port=1433,
            user="sa",
            password=os.getenv("DB_PASSWORD"),
            database="HrManagement"
          )
          cursor = conn.cursor()
          cursor.execute(query)
          rows = cursor.fetchall()
          conn.close()
          return str(rows)
        except Exception as e:
          return f"Query failed with error: {str(e)}"
    else:
        return "Unknown tool."

def run_test(test_case: TestCase, db_id: int, run_id: str):

    test_name = test_case.name
    prompt_text = build_prompt(test_case)

    MAX_ITERATIONS = 50
    iteration_count = 0

    screenshot_dir = os.path.join("screenshots", test_name, run_id)
    os.makedirs(screenshot_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        messages = [{"role": "user", "content": f"""Execute this test case step by step.

 Before clicking or typing anywhere, call read_page once after navigating to a new page or after a modal opens, and reuse that information for the following actions on the same view — you don't need to call it again unless the page has changed.

The database is Microsoft SQL Server (T-SQL syntax). Use TOP instead of LIMIT, e.g. SELECT TOP 1 * FROM Employees.

After any action that should create, update, or delete data, verify it actually happened by calling query_database with a SELECT query — do not conclude success based on the UI alone.

Take a screenshot after login, and once more immediately before calling finish_test.

IMPORTANT: You must end every test by calling the finish_test tool with your pass/fail verdict. Do not summarize the result in plain text — finish_test is the only valid way to report the outcome, and always make sure you mention if you verified the outcome also in the database. 

{prompt_text}"""}]

        while True:

            iteration_count += 1
            if iteration_count > MAX_ITERATIONS:
                print("TEST RESULT: BLOCKED")
                print(f"Reason: Exceeded {MAX_ITERATIONS} iterations without calling finish_test — likely stuck.")
                final_dir = os.path.join("screenshots", test_name, f"BLOCKED_TIMEOUT_{run_id}")
                os.rename(screenshot_dir, final_dir)
                browser.close()
                return

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                tools=TOOLS,
                messages=messages
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        if block.name == "finish_test":

                            test_result = block.input['result']
                            reason = block.input['reason']
                            print(f"TEST RESULT: {test_result}")
                            print(f"Reason: {reason}")
                            final_dir = os.path.join("screenshots", test_name, f"{test_result}_{run_id}")
                            os.rename(screenshot_dir, final_dir)
                            complete_run(db_id, test_result, reason, final_dir)
                            browser.close()
                            return

                        result = execute_tool(page, block.name, block.input, screenshot_dir)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                complete_run(db_id, "BLOCKED", "Agent stopped without calling finish_test.", screenshot_dir)
                browser.close()
                return
