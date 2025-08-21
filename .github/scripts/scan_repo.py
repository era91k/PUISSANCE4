#!/usr/bin/env python3
from pathlib import Path
import sys, math, json, re

root = Path(".").resolve()

# ---------- Utils ----------
def file_exists_any(paths: list[str]) -> bool:
    return any((root / p).exists() for p in paths)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

# ---------- Vérifications ----------
# Cadre de projet sécurisé
def check_security_md():
    return file_exists_any(["SECURITY.md", ".github/SECURITY.md"])

def check_contributing_md():
    return file_exists_any(["CONTRIBUTING.md", ".github/CONTRIBUTING.md"])

# Pilotage des incidents & vulnérabilités
def check_security_log_md():
    return file_exists_any(["SECURITY_LOG.md"])

def check_email_in_security_md():
    paths = ["SECURITY.md", ".github/SECURITY.md"]
    for p in paths:
        fp = root / p
        if fp.exists():
            txt = read_text(fp)
            if re.search(r"mailto:[^\s>\)]+", txt, re.IGNORECASE):
                return True
            if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", txt):
                return True
            if re.search(r"(?i)contact\s*[:\-]\s*[^\s,]+@[^,\s]+", txt):
                return True
    return False

# Conception sécurisée & automatisation
def check_cicd_pipeline():
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.exists():
        return False
    return any(wf_dir.glob("*.yml")) or any(wf_dir.glob("*.yaml"))

def check_automated_tests():
    if (root / "tests").exists():
        return True
    if list(root.glob("**/test_*.py")) or list(root.glob("**/*_test.go")):
        return True
    if list(root.glob("**/__tests__")) or list(root.glob("**/*.test.*")) or list(root.glob("**/*.spec.*")):
        return True
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(read_text(pkg))
            scripts = (data.get("scripts") or {})
            if any(k in scripts for k in ["test", "ci:test", "unit", "coverage"]):
                return True
        except Exception:
            pass
    wf_dir = root / ".github" / "workflows"
    if wf_dir.exists():
        for wf in list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")):
            content = read_text(wf).lower()
            if any(cmd in content for cmd in [
                "pytest", "npm test", "yarn test", "pnpm test",
                "jest", "vitest", "mocha", "mvn test", "gradle test", "go test"
            ]):
                return True
    return False

# Traitement correctif & diffusion
def check_changelog_md():
    return file_exists_any(["CHANGELOG.md", "CHANGELOG", "docs/CHANGELOG.md"])

def check_security_advisory_md():
    return file_exists_any(["SECURITY-ADVISORY.md", "SECURITY_ADVISORY.md"])

# ---------- Tableau ----------
SECTIONS = [
    ("`Cadre de projet sécurisé`", [
        ("SECURITY.md", check_security_md),
        ("CONTRIBUTING.md", check_contributing_md),
    ]),
    ("`Pilotage des incidents & vulnérabilités`", [
        ("SECURITY_LOG.md", check_security_log_md),
        ("Email de signalement défini (dans SECURITY.md)", check_email_in_security_md),
    ]),
    ("`Conception sécurisée & automatisation`", [
        ("Pipeline CI/CD", check_cicd_pipeline),
        ("Tests automatisés", check_automated_tests),
    ]),
    ("`Traitement correctif & diffusion`", [
        ("CHANGELOG.md", check_changelog_md),
        ("SECURITY-ADVISORY.md", check_security_advisory_md),
    ]),
]

def main():
    lines = []
    lines.append("| AXE | CRITÈRE VÉRIFIABLE | PRÉSENCE |")
    lines.append("|-----|---------------------|:-------:|")

    total = 0
    ok_count = 0

    # Pour stocker scores par axe
    per_axis_scores = []

    for section, checks in SECTIONS:
        first_row = True
        section_total = 0
        section_ok = 0

        for label, fn in checks:
            ok = fn()
            lines.append(f"| {section if first_row else ''} | {label} | {'✅' if ok else '❌'} |")
            total += 1
            ok_count += 1 if ok else 0
            section_total += 1
            section_ok += 1 if ok else 0
            first_row = False

        # Calcul score par axe
        section_percent = 0 if section_total == 0 else round(100 * section_ok / section_total)
        per_axis_scores.append((section, section_ok, section_total, section_percent))

    # Résumé global
    percent = 0 if total == 0 else round(100 * ok_count / total)
    filled = 0 if total == 0 else math.floor(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)
    status = "🟢 **Conforme**" if ok_count == total else "🔴 **Incomplet**"

    lines.append("")
    lines.append("### 📊 Scores par axe")
    for section, ok, tot, pct in per_axis_scores:
        bar_axis = "█" * math.floor(pct / 10) + "░" * (10 - math.floor(pct / 10))
        lines.append(f"- {section} : {ok}/{tot} — {pct}% `[ {bar_axis} ]`")

    lines.append("")
    lines.append("### 🧾 Bilan global")
    lines.append(f"- **Présents :** {ok_count} / {total}  —  **Manquants :** {total - ok_count}")
    lines.append(f"- **Progression :** `[ {bar} ]` {percent}%")
    lines.append(f"- **Statut :** {status}")

    print("\n".join(lines))
    sys.exit(0)

if __name__ == "__main__":
    main()
