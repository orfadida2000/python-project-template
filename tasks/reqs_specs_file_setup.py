import os
import re
import sys
import argparse
from enum import IntEnum

# strict: numbers only
STRICT_VERSION_RE = re.compile(r'^\d+(?:\.\d+)*$')

# wildcard: same as strict, but last part can be * or x
WILDCARD_VERSION_RE = re.compile(r'^\d+(?:\.\d+)*(?:\.\*)?$')

def is_valid_strict_version(v: str) -> bool:
	"""
	Validate a version string.
	Allows numeric versions (e.g. 1.2.3) and doesn't allow wildcard versions (e.g. 1.2.*).
	"""
	return bool(STRICT_VERSION_RE.match(v))

def is_valid_wildcard_version(v: str) -> bool:
	"""
	Validate a version string.
	Allows numeric versions (e.g. 1.2.3) and wildcard versions (e.g. 1.2.*).
	"""
	return bool(WILDCARD_VERSION_RE.match(v))

def compare_versions(v1: str, v2: str) -> int:
	"""Return -1 if v1 < v2, 0 if equal, +1 if v1 > v2 (wildcards forbidden here)."""
	nums1 = list(map(int, v1.split('.')))
	nums2 = list(map(int, v2.split('.')))
	return (nums1 > nums2) - (nums1 < nums2)


def is_valid_range_version(v_specs: str) -> bool:
	"""
	v_specs should have a structure of ver1,ver2 (e.g. 1.2.3,1.2.4).
	Validate a range is applicable (e.g. 1.2.3 < 1.2.4).
	Allows numeric versions (e.g. 1.2.3) and doesn't allow wildcard versions (e.g. 1.2.*).
	"""
	versions = v_specs.split(',')
	v1, v2 = versions[0].strip(), versions[1].strip()
	return is_valid_strict_version(v1) and is_valid_strict_version(v2) and compare_versions(v1, v2) < 0


class VersionSpec(IntEnum):
	"""
	Specification for versioning.
	"""
	EXACT = 1
	EXCLUDED = 2
	MINIMUM = 3
	MAXIMUM = 4
	RANGE = 5
	COMPATIBLE = 6
	LATEST = 7


def prompt_version_specifier_menu(package: str):

	print(f"\nSpecify version for package: {package}")
	print("Options:")
	print("1. Exact version (==, with optional wildcards like 1.2.*)")
	print("2. Excluded version (!=, with optional wildcards like 1.2.*)")
	print("3. Minimum version (>=, no optional wildcards allowed)")
	print("4. Maximum version (<=, no optional wildcards allowed)")
	print("5. Range (e.g. >=1.0,<2.0, no optional wildcards allowed)")
	print("6. Compatible release (~=, no optional wildcards allowed)")
	print("7. Latest stable release (no specifier)")


def prompt_choices(package: str) -> int:
	
	choice = -1
	while True:
		prompt_version_specifier_menu(package)
		try:
			choice = int(input("Enter option number (1-7): ").strip())
			if 1 <= choice <= 7:
				return choice
			print("Invalid choice. Please enter a number between 1 and 7.")
		except ValueError:
			print("Invalid input. Please enter a number between 1 and 7.")

def prompt_validate_specifier(choice: int) -> tuple[bool,str]:
	version_str = ""  
	spec = ""  # no specifier
	is_valid = False  # not valid
	if choice == VersionSpec.EXACT:
		version_str = input("Enter exact version (or with wildcard, e.g., 1.2.*): ").strip()
		spec = f"=={version_str}"
		is_valid = is_valid_wildcard_version(version_str)
	elif choice == VersionSpec.EXCLUDED:
		version_str = input("Enter excluded version (or with wildcard, e.g., 1.2.*): ").strip()
		spec = f"!={version_str}"
		is_valid = is_valid_wildcard_version(version_str)
	elif choice == VersionSpec.MINIMUM:
		version_str = input("Enter minimum version (e.g., 1.0): ").strip()
		spec = f">={version_str}"
		is_valid = is_valid_strict_version(version_str)
	elif choice == VersionSpec.MAXIMUM:
		version_str = input("Enter maximum version (e.g., 2.0): ").strip()
		spec = f"<={version_str}"
		is_valid = is_valid_strict_version(version_str)
	elif choice == VersionSpec.RANGE:
		min_version = input("Enter minimum version (e.g., 1.0): ").strip()
		max_version = input("Enter maximum version (e.g., 2.0): ").strip()
		version_str = f"{min_version},{max_version}"
		spec = f">={min_version},<{max_version}"
		is_valid = is_valid_range_version(version_str)
	elif choice == VersionSpec.COMPATIBLE:
		version_str = input("Enter base version for compatible release (e.g., 1.4): ").strip()
		spec = f"~={version_str}"
		is_valid = is_valid_strict_version(version_str)
	elif choice == VersionSpec.LATEST:
		is_valid = True

	return is_valid, spec


def ask_until_validated(choice: int) -> str:
	"""
	Keep asking the user for input until the validator returns True.
	"""
	while True:
		is_valid, spec = prompt_validate_specifier(choice)
		if is_valid:
			return spec
		print("Invalid specifier format, please try again.")


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

def is_commented_line(line: str) -> bool:
	return line.startswith("#")

def edit_reqs_file_specs(lines: list[str], version_spec_pkgs: set[str]) -> list[str]:
	new_lines = []
	for line in lines:
		if is_commented_line(line):
			new_lines.append(line)
			continue
		pkg = line  # line is a package name
		if pkg in version_spec_pkgs: 
			choice = prompt_choices(pkg)
			spec = ask_until_validated(choice)
		else:
			spec = ""  # no specifier
		new_lines.append(f"{pkg}{spec}")
	
	return new_lines


def comma_set(s: str) -> set[str]:
    # Explicit "" → empty set
    if s.strip() == "":
        return set()
    # Split, strip, and return unique values
    return {v.strip() for v in s.split(",") if v.strip()}

def return_version_spec_pkgs() -> set[str]:
	parser = argparse.ArgumentParser(description="Process version specifier packages.")
	parser.add_argument("spec_pkgs", 
					 	nargs="?",
					 	type=comma_set,
						default=set(), 
						help="Comma-separated list of packages (default: empty set)")
	args = parser.parse_args()
	return args.spec_pkgs



if __name__ == "__main__":
	lines = read_reqs_file()
	if not lines:
		print("No packages to process.")
		sys.exit(0)

	version_spec_pkgs = return_version_spec_pkgs()
	if not version_spec_pkgs:
		print("No packages specified for version specifiers. Exiting.")
		sys.exit(0)

	new_lines = edit_reqs_file_specs(lines, version_spec_pkgs)
	write_reqs_file(new_lines)
	print("requirements.txt updated with version specifiers.")
