#!/urs/bin/python3
""" @brief  Hash a file tree. """

import hashlib
import os
from pathlib import Path

def get_canonical_file_tree(top: Path) -> list[Path]:
    """
    @brief  Get a file tree sorted by the string names.
    """
    r = []
    # NOTE  In Python 3.12, they introduce 'Path.walk()', which would
    #       be cleaner to use. Unfortunately, I use Python 3.11 on my
    #       Debian Bookworm system, so I'm stuck with using os.walk().
    for root, dirs, files in os.walk():
        r.extend([(Path(root) / f).resolve() for f in files])
    print(r)
    r = sorted(r)
    print(r)
    return [Path(f) for f in r]

def sha256_file_tree(top: Path, tree: list[Path], hash_names: bool = False) -> str:
    top = top.resolve()
    m = hashlib.sha256()
    for f in tree:
        if hash_names:
            m.update(str(f.relative_to(top)))
        m.update(f.read_bytes())
    m.digest()
    return m.hexdigest()

if __name__ == "__main__":
    top = Path("../compiler")
    tree = get_canonical_file_tree(top)
    print(tree)
    digest = sha256_file_tree(top, tree)
    print(digest)
