#!/usr/bin/env bash
set -euo pipefail

# deps
sudo apt install -y curl jq

# where to put the templates (adjust as you like)
cd ~/python-project-template/

mkdir -p licenses/
cd licenses/

# fetch all license keys from GitHub
mapfile -t KEYS < <(curl -fsSL -H 'Accept: application/vnd.github+json' \
  https://api.github.com/licenses | jq -r '.[].key' | sort)

# helper: normalize placeholders to Copier variables
norm() {
  sed -E \
    -e 's/<YEAR>|\[year\]|\{year\}|\[yyyy\]|<year>|\(year\)/{{ current_year }}/g' \
    -e 's/<OWNER>|\[owner\]|\[fullname\]|<name of author>|<copyright holders>|<COPYRIGHT HOLDER>|<COPYRIGHT HOLDERS>|<copyright holder>|\(name of author\)/{{ author_name }}/g'
}

# download each template and normalize
for key in "${KEYS[@]}"; do
  echo "• ${key}"
  body="$(curl -fsSL -H 'Accept: application/vnd.github+json' \
          "https://api.github.com/licenses/${key}" | jq -r '.body')"
  # save as Jinja template for Copier
  printf "%s" "$body" | norm > "LICENSE-${key}.jinja"
done

echo "Done. Templates in $(pwd)"

