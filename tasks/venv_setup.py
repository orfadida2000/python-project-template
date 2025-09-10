"""
tasks/setup_venv.py
- Use active venv if present; else prefer/create .venv
- Upgrade pip
- If requirements.txt exists -> pip install [-U] -r requirements.txt
- Else:
	* default: install only missing baseline pkgs
	* --upgrade: install --upgrade baseline pkgs (latest)
"""

import os
import sys
import argparse
import subprocess
import venv
import platform
from importlib import metadata

def in_venv(proj_dir: str) -> bool:
	"""
	True only if an activated venv is inside this project.
	Uses VIRTUAL_ENV and ensures it sits under proj_dir.
	"""
	venv_root = os.environ.get("VIRTUAL_ENV")
	if not venv_root:
		return False
	try:
		proj_abs = os.path.abspath(proj_dir)
		venv_abs = os.path.abspath(venv_root)
		return os.path.commonpath([proj_abs, venv_abs]) == proj_abs
	except ValueError:
		return False

def run(cmd: list[str]) -> None:
	subprocess.check_call(cmd)


def venv_python_path(vdir: str) -> str:
	if platform.system().lower() == "windows":
		return os.path.join(vdir, "Scripts", "python.exe")
	return os.path.join(vdir, "bin", "python")


def print_activation_help(proj_dir: str):
	system = platform.system().lower()
	if system == "windows":
		ps1 = os.path.join(proj_dir, ".venv", "Scripts", "Activate.ps1")
		bat = os.path.join(proj_dir, ".venv", "Scripts", "activate.bat")
		print(f"\nTo activate (PowerShell):\n  {ps1}")
		print(f"To activate (cmd.exe):\n  {bat}\n")
	else:
		sh = os.path.join(proj_dir, ".venv", "bin", "activate")
		fish = os.path.join(proj_dir, ".venv", "bin", "activate.fish")
		print(f"\nTo activate (bash/zsh):\n  source {sh}")
		if os.path.exists(fish):
			print(f"To activate (fish):\n  source {fish}")
		print()


def parse_args(argv: list[str]) -> argparse.Namespace:
	p = argparse.ArgumentParser(add_help=False)
	# One simple flag to mirror your old env toggle
	p.add_argument("--upgrade", action="store_true")
	# allow unknown so Copier’s runner can append things without breaking
	args, _ = p.parse_known_args(argv)
	return args


def main():
	args = parse_args(sys.argv[1:])

	proj_dir = os.getcwd()
	vdir = os.path.join(proj_dir, ".venv")

	active_now = in_venv(proj_dir)
	need_activation = not active_now

	# Choose interpreter
	if active_now:
		print("Active project virtualenv detected; using it.")
		py = sys.executable
	else:
		if not os.path.exists(vdir):
			print("No active project virtualenv; creating .venv ...")
			try:
				venv.EnvBuilder(with_pip=True).create(vdir)
			except Exception as e:
				print(f"Error creating virtualenv: {e}")
				sys.exit(0)
		py = venv_python_path(vdir)
		print(f"Using interpreter: {py}")

	try:
		# Ensure pip is up to date
		run([py, "-m", "pip", "install", "--upgrade", "pip"])
	except:
		print("Error upgrading pip; continuing anyway.")

	# Upgrade mode via CLI flag
	upgrade = args.upgrade
	print(f"Upgrade mode: {'ON (--upgrade)' if upgrade else 'OFF (install missing only)'}")

	# Install from requirements.txt if present
	req_file = os.path.join(proj_dir, "requirements.txt")
	if os.path.isfile(req_file): 
		print(f"Installing from {req_file} ...")
		if os.path.getsize(req_file) > 0:
			cmd = [py, "-m", "pip", "install"]
			if upgrade:
				cmd.append("--upgrade")
			cmd.extend(["-r", req_file])
			try:
				run(cmd)
			except subprocess.CalledProcessError as e:
				print(f"Error installing from {req_file}: {e}")
				sys.exit(0)
		else:
			print(f"No packages found in {req_file}; skipping installation.")
	else:  # copier didnt create/overwrite requirements.txt (only happens when the user specify it)
		print("No requirements.txt found; skipping installation.")

	if need_activation:
		print_activation_help(proj_dir)
	else:
		print("\nEnvironment ready (installed into the active virtualenv).\n")


if __name__ == "__main__":
	main()