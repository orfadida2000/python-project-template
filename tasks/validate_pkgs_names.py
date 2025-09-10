import os
import sys
import urllib.request
import urllib.error

def pypi_package_exists(package_name: str) -> bool:
	"""
	Checks if a PyPI package name exists.

	Args:
		package_name (str): The name of the package to check.

	Returns:
		bool: True if the package exists, False otherwise.
	"""

	pypi_url = f"https://pypi.org/pypi/{package_name}/json"
	try:
		with urllib.request.urlopen(pypi_url) as response:
			# If the response is successful (e.g., 200 OK), the package exists.
			return True
	except urllib.error.HTTPError as e:
		if e.code == 404:
			# A 404 error indicates the package does not exist.
			return False
		else:
			# Other HTTP errors indicate a problem, but not necessarily non-existence.
			print(f"Error accessing PyPI for {package_name}: {e}")
			return False
	except urllib.error.URLError as e:
		# Network-related errors (e.g., no internet connection)
		print(f"Network error while checking {package_name}: {e}")
		return False

def read_reqs_file() -> list[str]:
	if not os.path.isfile("requirements.txt"):
		print("requirements.txt not found in current directory.")
		sys.exit(0)
	try:
		with open("requirements.txt", "r") as f:
			packages = [line.strip() for line in f if line.strip()]
	except Exception as e:
		print(f"Error reading requirements.txt: {e}")
		sys.exit(0)
	return packages

def write_reqs_file(new_lines: list[str]) -> None:
	try:
		with open("requirements.txt", "w") as f:
			f.write("\n".join(new_lines))
	except Exception as e:
		print(f"Error writing to requirements.txt: {e}")
		sys.exit(0)

def validate_reqs_pkgs(packages: list[str]) -> list[str]:
	new_lines = []
	for pkg in packages:
		if pypi_package_exists(pkg) and pkg not in ["pip", "pip3"]:
			new_lines.append(pkg)
		else:
			new_lines.append(f"# {pkg} - Invalid package name")
			print(f"Package '{pkg}' does not exist on PyPI. Marked as invalid in requirements.txt.")
	return new_lines

if __name__ == "__main__":
	packages = read_reqs_file()
	if not packages:
		print("No packages to validate.")
		sys.exit(0)

	new_lines = validate_reqs_pkgs(packages)
	write_reqs_file(new_lines)
	print("requirements.txt updated successfully (validation complete).")
