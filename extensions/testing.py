from jinja2.ext import Extension

def test_valid(s: str) -> str:
	if s.strip().lower() == "error":
		return "error"
	return ""


class TestingExtension(Extension):
	def __init__(self, environment):
		super().__init__(environment)
		environment.filters["test_valid"] = test_valid