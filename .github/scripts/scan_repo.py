#!/usr/bin/env python3
from pathlib import Path
import sys, math, json, re

root = Path(".").resolve()

# ---------- Utils de base ----------
def file_exists_any(paths: list[str]) -> tuple[bool, str]:
    """Retourne (True, chemin_trouvé) si un des chemins existe."""
    for p in paths:
        path = root / p
        if path.exists():
            return True, p
    return False, ""

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

# ---------- 4 catégories / 8 critères ----------
# Cadre de projet sécurisé
def check_security_md():
    ok, where = file_exists_any(["SECURITY.md", ".github/SECURITY.md"])
    return ok, (f"Trouvé à `{where}`" if ok else "Manquant")

def check_contributing_md():
    ok, where = file_exists_any(["CONTRIBUTING.md", ".github/CONTRIBUTING.md"])
    return ok, (f"Trouvé à `{where}`" if ok else "Manquant")

# Pilotage des incidents & vulnérabilités
def check_security_log_md():
    ok, where = file_exists_any(["SECURITY_LOG.md"])
    return ok, (f"Trouvé à `{where}`" if ok else "Manquant")

def parse_email_from_security_md():
    ok, where = file_exists_any(["SECURITY.md", ".github/SECURITY.md"])
    if not ok:
        return False, "SECURITY.md absent"
    txt = read_text((root / where))
    # mailto:
    m = re.search(r"mailto:([^\s>\)]+)", txt, re.IGNORECASE)
    if m:
        return True, f"Email détecté : `{m.group(1)}`"
    # email générique
    m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", txt)
    if m:
        return True, f"Email détecté : `{m.group(0)}`"
    # contact: email
    m = re.search(r"(?i)contact\s*[:\-]\s*([^\s,]+@[^,\s]+)", txt)
    if m:
        return True, f"Email détecté : `{m.group(1)}`"
    return False, "Aucun email ou `mailto:` détecté dans SECURITY.md"

# Conception sécurisée & automatisation
def check_cicd_pipeline():
    # au moins un workflow YAML/YML dans .github/workflows
    has_dir = (root / ".github" / "workflows").exists()
    if not has_dir:
        return False, "Dossier `.github/workflows` absent"
    patterns = ["*.yml", "*.yaml"]
    for pat in patterns:
        if any((root / ".github" / "workflows").glob(pat)):
            return True, "Workflow GitHub Actions détecté"
    return False, "Aucun workflow `.yml|.yaml` dans `.github/workflows`"

def check_automated_tests():
    # heuristiques multi-ecosystèmes
    found_signals = []

    # 1) Dossiers/fichiers de tests courants
    if (root / "tests").exists():
        found_signals.append("dossier `tests/`")
    if list(root.glob("**/test_*.py")) or list(root.glob("**/*_test.go")):
        found_signals.append("fichiers de tests (py/go)")
    if list(root.glob("**/__tests__")) or list(root.glob("**/*.test.*")) or list(root.glob("**/*.spec.*")):
        found_signals.append("fichiers de tests (js/ts)")

    # 2) package.json → script test
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(read_text(pkg))
            scripts = (data.get("scripts") or {})
            if any(k in scripts for k in ["test", "ci:test", "unit", "coverage"]):
                found_signals.append("script `npm/yarn/pnpm test`")
        except Exception:
            pass

    # 3) Workflows qui lancent des tests (recherche de mots-clés)
    wf_dir = root / ".github" / "workflows"
    if wf_dir.exists():
        for wf in list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")):
            content = read_text(wf).lower()
            if any(cmd in content for cmd in [
                "pytest", "nose", "tox",
                "npm test", "yarn test", "pnpm test",
                "jest", "vitest", "mocha",
                "mvn test", "gradle test", "go test", "pytest -q"
            ]):
                found_signals.append(f"workflow exécute des tests ({wf.name})")
                break

    if found_signals:
        return True, " / ".join(found_signals)
    return False, "Aucun indicateur clair de tests automatisés"

# Traitement correctif & diffusion
def check_changelog_md():
    ok, where = file_exists_any(["CHANGELOG.md", "CHANGELOG", "docs/CHANGELOG.md"])
    return ok, (f"Trouvé à `{where}`" if ok else "Manquant")

def check_security_advisory_md():
    ok, where = file_exists_any(["SECURITY-ADVISORY.md", "SECURITY_ADVISORY.md"])
    return ok, (f"Trouvé à `{where}`" if ok else "Manquant")

# ---------- Rendu tableau + bilan ----------
SECTIONS = [
    ("Cadre de projet sécurisé", [
        ("SECURITY.md", check_security_md),
        ("CONTRIBUTING.md", check_contributing_md),
    ]),
    ("Pilotage des incidents & vulnérabilités", [
        ("SECURITY_LOG.md", check_security_log_md),
        ("Email de signalement défini (dans SECURITY.md)", parse_email_from_security_md),
    ]),
    ("Conception sécurisée & automatisation", [
        ("Pipeline CI/CD", check_cicd_pipeline),
        ("Tests automatisés", check_automated_tests),
    ]),
    ("Traitement correctif & diffusion", [
        ("CHANGELOG.md", check_changelog_md),
        ("SECURITY-ADVISORY.md", check_security_advisory_md),
    ]),
]

def main():
    lines = []
    lines.append("| AXE                               | CRITÈRE VÉRIFIABLE                            | PRÉSENCE | DÉTAIL |")
    lines.append("|-----------------------------------|-----------------------------------------------|:-------:|--------|")

    total = 0
    ok_count = 0

    for section, checks in SECTIONS:
        first_row = True
        for label, fn in checks:
            ok, detail = fn()
            lines.append(f"| {section if first_row else ''} | {label} | {'✅' if ok else '❌'} | {detail} |")
            total += 1
            ok_count += 1 if ok else 0
            first_row = False

    # Bilan global
    percent = 0 if total == 0 else round(100 * ok_count / total)
    filled = 0 if total == 0 else math.floor(percent / 10)  # 10 segments
    bar = "█" * filled + "░" * (10 - filled)
    status = "🟢 **Conforme**" if ok_count == total else "🔴 **Incomplet**"

    lines.append("")
    lines.append("### 🧾 Bilan")
    lines.append(f"- **Présents :** {ok_count} / {total}  —  **Manquants :** {total - ok_count}")
    lines.append(f"- **Score :** {percent}%")
    lines.append(f"- **Progression :** `[ {bar} ]` {percent}%")
    lines.append(f"- **Statut :** {status}")

    print("\n".join(lines))
    sys.exit(0 if ok_count == total else 1)

if __name__ == "__main__":
    main()
