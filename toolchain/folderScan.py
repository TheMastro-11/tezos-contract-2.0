from pathlib import Path

def folderScan(path):
    """Return a list of contract targets found in the given contracts directory.

    Each returned item is a string identifier in the form:
        <ContractFolder>:<PythonFileBaseName>

    This keeps backward compatibility with the previous behavior (folder names only),
    while allowing multiple implementations per contract folder (e.g. *Rosetta.py).

    The returned list is sorted for stable UX.
    """
    contracts_path = Path(path)

    targets = []
    for entry in contracts_path.iterdir():
        if not entry.is_dir():
            continue

        folder_name = entry.name

        # Skip hidden/system folders
        if folder_name.startswith('.'):
            continue

        # Add each top-level .py file as a selectable target
        for py_file in sorted(entry.glob('*.py')):
            file_base = py_file.stem
            if file_base.startswith('.'):
                continue
            targets.append(f"{folder_name}:{file_base}")

        # Backward compatibility: if no .py files are found, keep folder name
        if not any(entry.glob('*.py')):
            targets.append(folder_name)

    return sorted(targets)
