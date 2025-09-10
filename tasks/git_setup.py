#!/usr/bin/env python3
"""
Initialize a local Git repo on branch 'main' if possible.
- Never exit with non-zero status (safe for Copier). Prints status messages only.
"""

import argparse
import subprocess


def has_git() -> bool:
	"""Return True if the `git` binary exists and runs."""
	try:
		p = subprocess.run(
			["git", "--version"],
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
		return p.returncode == 0
	except (FileNotFoundError, OSError):
		return False


def is_inside_git_worktree() -> bool:
	"""
	True iff we're inside a non-bare Git worktree.
	Bare repos return rc=0 but print 'false'.
	"""
	p = subprocess.run(
		["git", "rev-parse", "--is-inside-work-tree"],
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL,
		text=True,
	)
	return p.returncode == 0 and p.stdout.strip() == "true"


def init_git_repo_main_branch(branch: str) -> bool:
	"""
	Initialize repo on 'main' across Git versions, returning True on success.
	Uses return codes (no exceptions) and silences command output.
	"""
	# 1) Modern Git (>=2.28): one-shot init on 'main'
	rc = subprocess.run(
		["git", "init", "-b", branch],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	).returncode
	if rc == 0:
		return True

	# 2) Older Git: plain init
	rc = subprocess.run(
		["git", "init"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	).returncode
	if rc != 0:
		return False

	# Try to point HEAD to main cleanly
	rc = subprocess.run(
		["git", "symbolic-ref", "HEAD", f"refs/heads/{branch}"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	).returncode
	if rc == 0:
		return True

	# 3) Ancient fallback: create/switch via checkout
	rc = subprocess.run(
		["git", "checkout", "-b", branch],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	).returncode
	return rc == 0

def branch_name(s: str) -> str:
	if s.strip() == "":
		return "main"
	return s.strip()

def get_branch_name() -> str:
	parser = argparse.ArgumentParser(description="Get initial branch name.")
	parser.add_argument("branch", 
					 	nargs="?", 
						type=branch_name, 
						default="main", 
						help="Initial branch name (default: 'main')")
	args = parser.parse_args()
	return args.branch

def main() -> int:
	# 0. Ensure git exists
	if not has_git():
		print("git not found; skipping init.")
		return 0  # Always succeed (don’t break Copier)
	# 1. Avoid re-initializing existing repos
	if is_inside_git_worktree():
		print("Git repo already present; skipping.")
		return 0
	# 2. Get desired branch name
	branch = get_branch_name()
	# 3. Try to init on 'main' (across versions)
	if init_git_repo_main_branch(branch):
		print("Initialized empty Git repository on branch 'main'.")
	else:
		# Likely permissions, read-only FS, etc. Don’t fail the process.
		print("Failed to initialize Git repository.")
	return 0  # Always 0 by requirement


if __name__ == "__main__":
	main()