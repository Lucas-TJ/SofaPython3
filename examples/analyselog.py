import os
import re
from collections import defaultdict

LOG_ROOT = "/home/lburel/logs/run_062"


def extract_stderr(content):
    if "=== STDERR ===" not in content:
        return ""

    part = content.split("=== STDERR ===", 1)[1]

    if "=== DURATION ===" in part:
        part = part.split("=== DURATION ===", 1)[0]

    return part.strip()


def normalize_error(stderr):
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]

    # On garde les lignes les plus significatives
    significant = []

    for line in lines:
        # Ignore les lignes "File ... line ..."
        if line.startswith("File "):
            continue

        # Remplace les chemins absolus
        line = re.sub(r"/[^\s:]+", "<PATH>", line)

        # Remplace les numéros
        line = re.sub(r"\b\d+\b", "<N>", line)

        significant.append(line)

    # Si possible, garder la dernière ligne (souvent le message principal)
    if significant:
        return significant[-1]

    return "Unknown error"


def main():
    groups = defaultdict(list)

    for filename in os.listdir(LOG_ROOT):
        if not filename.endswith(".log"):
            continue

        path = os.path.join(LOG_ROOT, filename)

        with open(path, "r", errors="ignore") as f:
            content = f.read()

        stderr = extract_stderr(content)

        if not stderr.strip():
            continue

        signature = normalize_error(stderr)
        groups[signature].append(filename)

    # Trier par fréquence décroissante
    sorted_groups = sorted(
        groups.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    for signature, files in sorted_groups:
        print("=" * 80)
        print(f"{len(files)} occurrences")
        print(f"Signature : {signature}")
        print("Examples:")
        for f in files[:10]:
            print("  -", f)
        print()


if __name__ == "__main__":
    main()