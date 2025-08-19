#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(".")

CHECKS = [
    ("GOUVERNANCE / PREVENTION", "SECURITY.md présent", ["SECURITY.md"]),
    ("", "CONTRIBUTING.md présent", ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]),
    ("", "CODEOWNERS présent", ["CODEOWNERS", ".github/CODEOWNERS"]),
    ("", "Protection des branches activée", []),  # TODO: API GitHub
    ("", "Modèle de PR (PULL_REQUEST_TEMPLATE.md) présent",
     ["PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"]),
    ("", "Commits signés (GPG)", []),  # TODO: vérification via API
    ("GOUVERNANCE / REACTION", "SECURITY_LOG.md présent", ["SECURITY_LOG.md"]),
    ("TECHNIQUE / PREVENTION", "README.md présent", ["README.md"]),
    ("TECHNIQUE / REACTION", "CHANGELOG.md présent", ["CHANGELOG.md", "CHANGELOG", "docs/CHANGELOG.md"]),
]

def find_first(paths):
    for p in paths:
        if (root / p).exists():
            return True
    return False

lines = []
lines.append("| AXE                   | CRITÈRE VÉRIFIABLE                         | PRÉSENCE |")
lines.append("|------------------------|---------------------------------------------|:--------:|")

missing = False
for category, label, candidates in CHECKS:
    if not candidates:  # Placeholder pour vérifs API
        ok = "❌"
        missing = True
    else:
        if find_first(candidates):
            ok = "✅"
        else:
            ok = "❌"
            missing = True
    lines.append(f"| {category} | {label} | {ok} |")

print("\n".join(lines))
sys.exit(1 if missing else 0)
