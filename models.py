from dataclasses import dataclass

@dataclass
class TestCase:
    name: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str
