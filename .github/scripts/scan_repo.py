#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(".")

checks = [
    ("README.md", "README.md présent à la racine du dépôt."),
    ("SECURITY.md", "SECURITY.md présent à la racine du dépôt."),
]

missing = False

for filename, success_msg in checks:
    file_path = root / filename
    if file_path.exists():
        print(f"✅ {success_msg}")
    else:
        print(f"❌ {filename} manquant à la racine du dépôt.")
        missing = True

# Si au moins un fichier requis est manquant → échec
sys.exit(1 if missing else 0)
