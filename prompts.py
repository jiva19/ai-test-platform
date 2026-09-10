from models import TestCase

def build_prompt(test_case: TestCase) -> str:
    preconditions_text = "\n".join(f"- {p}" for p in test_case.preconditions)
    steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(test_case.steps, 1))
    return f"""Test Case: {test_case.name}

Preconditions:
{preconditions_text}

Steps:
{steps_text}

Expected Result:
{test_case.expected_result}"""
