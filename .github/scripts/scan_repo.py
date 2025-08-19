#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(".")

CHECKS = [
    ("README.md",                ["README.md"]),
    ("SECURITY.md",              ["SECURITY.md"]),
    ("CONTRIBUTING.md",          ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]),
    ("CODEOWNERS",               ["CODEOWNERS", ".github/CODEOWNERS"]),
    ("PULL_REQUEST_TEMPLATE.md", ["PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE.md"]),
    ("SECURITY_LOG.md",          ["SECURITY_LOG.md"]),
    ("CHANGELOG.md",             ["CHANGELOG.md"]),
]

def find_first(paths):
    for p in paths:
        if (root / p).exists():
            return p
    return None

rows = []
missing = False

# En-tête
print("| Fichier | Présent | Détail |")
print("|---------|:-------:|--------|")

for display_name, candidates in CHECKS:
    found = find_first(candidates)
    if found:
        rows.append((f"`{display_name}`", "✅", f"Trouvé à `{found}`"))
    else:
        rows.append((f"`{display_name}`", "❌", "Manquant"))
        missing = True

# Lignes
for name, ok, detail in rows:
    print(f"| {name} | {ok} | {detail} |")

sys.exit(1)
