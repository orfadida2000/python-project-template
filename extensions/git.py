#!/usr/bin/env python3

from jinja2.ext import Extension
import re


def validate_github_username(name: str) -> str:
	"""
	Return an error string if invalid; empty string if valid.
	Empty input is allowed (optional field).
	"""
	GH_RE = re.compile(r'^[a-z0-9](?:[a-z0-9]|-(?=[a-z0-9])){0,38}$')
	if name is None:
		return ""  # optional

	s = name.strip().lower()

	# Optional field: empty is valid
	if not s:
		return ""

	if GH_RE.fullmatch(s) is None:
		return ("GitHub username may only contain letters, digits, and single hyphens. "
				"It must have no leading/trailing hyphen, no consecutive hyphens, "
				"and be at most 39 chars.")

	return ""

def validate_branch_name(name: str) -> str:
	"""
	Validate a Git branch name (Unicode allowed; enforce Git's ref rules subset).

	Usage (CLI):
		python validate_branch.py <name>

	Behavior:
		- Returns the FIRST matching error message string.
		- Returns "" (empty string) if the name is valid.
	"""
	if name is None:
		return ""

	s = name.strip()

	# Empty
	if not s:
		return ""

	# Reserved exact name
	if s == "@":
		return "'@' is reserved."

	# Disallowed suffix
	if s.endswith(".lock"):
		return "Branch name cannot end with '.lock'."

	# Disallowed start/end chars
	if s.startswith("/"):
		return "Branch name cannot start with '/'."
	if s.endswith("/"):
		return "Branch name cannot end with '/'."
	if s.startswith("."):
		return "Branch name cannot start with '.'."
	if s.endswith("."):
		return "Branch name cannot end with '.'."
	if s.startswith("-"):
		return "Branch name cannot start with '-'."
	if s.endswith("-"):
		return "Branch name cannot end with '-'."

	# Disallowed sequences
	if "//" in s:
		return "Branch name cannot contain '//' (no consecutive slashes)."
	if ".." in s:
		return "Branch name cannot contain '..'."
	if "@{" in s:
		return "Branch name cannot contain '@{'."

	# Disallowed individual characters
	forbidden_chars = {"\\", "?", "[", "]", "*"}
	if any(c in s for c in forbidden_chars):
		return "Branch name cannot contain: \\ ? [ ] *"

	# Control characters, DEL, or any whitespace (space, tab, etc.)
	if any(ord(c) < 32 or ord(c) == 127 or c.isspace() for c in s):
		return "Branch name cannot contain control characters or whitespace."

	# Passed all checks
	return ""

class GitExtension(Extension):
	def __init__(self, environment):
		super().__init__(environment)
		environment.filters["validate_branch_name"] = validate_branch_name
		environment.filters["validate_github_username"] = validate_github_username