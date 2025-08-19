#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(".")

# Pour certains fichiers, GitHub accepte plusieurs emplacements usuels.
CHECKS = [
    ("README.md",                ["README.md"]),
    ("SECURITY.md",              ["SECURITY.md"]),
    ("CONTRIBUTING.md",          ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]),
    ("CODEOWNERS",               ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"]),
    ("PULL_REQUEST_TEMPLATE.md", ["PULL_REQUEST_TEMPLATE.md",
                                  ".github/PULL_REQUEST_TEMPLATE.md",
                                  ".github/pull_request_template.md"]),
    ("SECURITY_LOG.md",          ["SECURITY_LOG.md"]),
    ("CHANGELOG.md",             ["CHANGELOG.md", "CHANGELOG", "docs/CHANGELOG.md"]),
]

rows = []
missing = False

def find_first(paths):
    for p in paths:
        path = root / p
        if path.exists():
            return p
    return None

# En-tête du tableau Markdown
print("| Fichier | Présent | Détail |")
print("|---|:---:|---|")

for display_name, candidates in CHECKS:
    found_at = find_first(candidates)
    if found_at:
        rows.append((display_name, "✅", f"Trouvé à `{found_at}`"))
    else:
        rows.append((display_name, "❌", "Manquant"))
        missing = True

# Lignes du tableau
for name, ok, detail in rows:
    print(f"| `{name}` | {ok} | {detail} |")

# Si au moins un fichier requis manque, code de sortie 1 pour faire échouer le job
sys.exit(1 if missing else 0)
