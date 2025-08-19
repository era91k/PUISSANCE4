#!/usr/bin/env python3
from pathlib import Path
import sys
import math

root = Path(".")

CHECKS = [
    ("README.md",                ["README.md"]),
    ("SECURITY.md",              ["SECURITY.md"]),
    ("CONTRIBUTING.md",          ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]),
    ("CODEOWNERS",               ["CODEOWNERS", ".github/CODEOWNERS"]),
    ("PULL_REQUEST_TEMPLATE.md", ["PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"]),
    ("SECURITY_LOG.md",          ["SECURITY_LOG.md"]),
    ("CHANGELOG.md",             ["CHANGELOG.md", "CHANGELOG", "docs/CHANGELOG.md"]),
]

def find_first(paths: list[str]) -> str | None:
    for p in paths:
        if (root / p).exists():
            return p
    return None

rows = []
present = 0
missing = 0

# --- Tableau ---
lines = []
lines.append("| Fichier | Présent | Détail |")
lines.append("|---------|:-------:|--------|")

for display_name, candidates in CHECKS:
    found = find_first(candidates)
    if found:
        rows.append((f"`{display_name}`", "✅", f"Trouvé à `{found}`"))
        present += 1
    else:
        rows.append((f"`{display_name}`", "❌", "Manquant"))
        missing += 1

for name, ok, detail in rows:
    lines.append(f"| {name} | {ok} | {detail} |")

# --- Bilan visuel ---
total = present + missing
percent = 0 if total == 0 else round(100 * present / total)
# barre sur 10 segments
filled = 0 if total == 0 else math.floor(percent / 10)
bar = "█" * filled + "░" * (10 - filled)
status = "🟢 **Conforme**" if missing == 0 else "🔴 **Incomplet**"

lines.append("")
lines.append("### 🧾 Bilan")
lines.append(f"- **Présents :** {present} / {total} &nbsp;&nbsp;—&nbsp;&nbsp; **Manquants :** {missing}")
lines.append(f"- **Score :** {percent}%")
lines.append(f"- **Progression :** `[ {bar} ]` {percent}%")
lines.append(f"- **Statut :** {status}")

print("\n".join(lines))

# Échec si au moins un fichier manque
sys.exit(0 if missing == 0 else 1)
