from pathlib import Path

from bot.caches.paths import Paths


IGNORE = {".git", ".idea", ".ruff_cache", ".venv", "__pycache__", "backups", "scripts"}

tree, files = [], []


def walk_paths(path: Path, prefix: str = "") -> None:
    paths = sorted(
        (p for p in path.iterdir() if p.name not in IGNORE),
        key=lambda p: (p.is_file(), p.name.lower()),
    )

    for i, p in enumerate(paths, 1):
        tree.append(f"{prefix}{'└── ' if i == len(paths) else '├── '}{p.name}")

        if p.is_dir():
            walk_paths(p, prefix + ("    " if i == len(paths) else "│   "))
        elif p.suffix in {".py", ".yaml", ".conf"} and p.stem != "__init__":
            with open(p, encoding="utf-8") as f:
                files.append(f"# {'=' * 77}\n# {p.name}\n\n{f.read()}")


if __name__ == "__main__":
    walk_paths(Paths.ROOT)
    print("\n".join(tree), "\n".join(files), sep="\n\n")
