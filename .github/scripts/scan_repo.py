#!/usr/bin/env python3
from pathlib import Path
import sys, math

root = Path(".")

CHECKS = [
    ("GOUVERNANCE / PREVENTION", "SECURITY.md présent", ["SECURITY.md"]),
    ("", "CONTRIBUTING.md présent", ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]),
    ("", "CODEOWNERS présent", ["CODEOWNERS", ".github/CODEOWNERS"]),
    ("", "Protection des branches activée", []),  # TODO via API
    ("", "Modèle de PR (PULL_REQUEST_TEMPLATE.md) présent",
     ["PULL_REQUEST_TEMPLATE.md", ".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"]),
    ("", "Commits signés (GPG)", []),  # TODO via API
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

present = 0
missing = 0

for category, label, candidates in CHECKS:
    if not candidates:  # Placeholder pour vérifs API
        ok = "❌"
        missing += 1
    else:
        if find_first(candidates):
            ok = "✅"
            present += 1
        else:
            ok = "❌"
            missing += 1
    lines.append(f"| {category} | {label} | {ok} |")

# --- Bilan visuel ---
total = present + missing
percent = 0 if total == 0 else round(100 * present / total)
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

sys.exit(1 if missing else 0)
