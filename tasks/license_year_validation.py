# tasks/license_year_validator.py
# Validate --year is an int and within 1970..current calendar year.

import sys
import argparse
import datetime
from typing import List

def main(argv: List[str]) -> int:
	parser = argparse.ArgumentParser(
		prog="license_year_validator.py",
		description="Validate a year is within 1970-current calendar year."
	)
	parser.add_argument(
		"--year",
		type=int,            # enforce integer conversion
		required=True,       # must be provided
		metavar="YYYY",
		help="Year to validate (e.g., 2025)"
	)

	# Let argparse do type/required checks; add our own hint on failure
	try:
		args = parser.parse_args(argv)
	except SystemExit as exc:
		if exc.code != 0:
			sys.stderr.write("Usage: license_year_validator.py --year YYYY\n")
		return 2

	y = args.year  # already an int
	now = datetime.date.today().year
	if not (1970 <= y <= now):
		sys.stderr.write(f"Error: year {y} must be between 1970 and {now}.\n")
		return 1

	print(f"license_year OK: {y}")
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))