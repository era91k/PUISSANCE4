#!/usr/bin/env python3
from pathlib import Path
import sys

readme = Path("README.md")

if readme.exists():
    print("✅ README.md présent à la racine du dépôt.")
    sys.exit(0)
else:
    print("❌ README.md manquant à la racine du dépôt.")
    sys.exit(1)  # fait échouer le workflow
