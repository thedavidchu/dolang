#!/urs/bin/python3
""" @brief  Cryptographically hash a file tree. """

import hashlib
import os
from pathlib import Path
from warnings import warn


def track_definite_cycle(path_set: set, p: Path):
    p = p.absolute()
    if p in path_set:
        raise ValueError(f"cycle involving {p}")
    path_set.add(p)


def track_potential_cycle(path_set: set, x: Path):
    x = x.resolve()
    if x in path_set:
        warn(f"{x} already in set; may have encountered a cycle!")
    path_set.add(x)


def get_canonical_file_tree(top: Path) -> list[Path]:
    """
    @brief  Get a file tree sorted by the string names.
    @note   I don't fully resolve paths in the tree because I want to
            use the path as the user sees rather than symbolic links.
            This means that my cycle detection won't work because if I
            don't resolve the paths, then I wouldn't see repeat paths;
            they'll just get longer and longer as I add more symlinks.
    @todo   Sort the files more intelligently, e.g. in a Merkle Tree.
    """
    # Tree without resolving the symlinks.
    tree = set()
    # Tree of real, absolute paths.
    real_tree = set()
    # NOTE  In Python 3.12, they introduce 'Path.walk()', which would
    #       be cleaner to use. Unfortunately, I use Python 3.11 on my
    #       Debian Bookworm system, so I'm stuck with using os.walk().
    for root, dirs, files in os.walk(top):
        for d in dirs:
            path = Path(root) / d
            track_definite_cycle(tree, path)
            # This is redundant from tracking definite cycles, but I
            # like to be explicit.
            tree.add(path.absolute())
            track_potential_cycle(real_tree, path)
        for f in files:
            path = Path(root) / f
            # This is redundant from tracking definite cycles, but I
            # like to be explicit.
            track_definite_cycle(tree, path)
            tree.add(path.absolute())
            track_potential_cycle(real_tree, path)
    tree = sorted(tree)
    return tree


def sha256_file_tree(top: Path, tree: list[Path], hash_path: bool = False) -> str:
    top = top.absolute()
    m = hashlib.sha256()
    for f in tree:
        assert f.exists()
        rel_path = f.relative_to(top)
        if f.is_file():
            if hash_path:
                m.update(str(rel_path).encode())
            m.update(f.read_bytes())
            continue
        if f.is_dir():
            if hash_path:
                m.update(str(rel_path).encode())
            continue
    m.digest()
    return m.hexdigest()


if __name__ == "__main__":
    top = Path("../compiler")
    tree = get_canonical_file_tree(top)
    digest = sha256_file_tree(top, tree, False)
    print("Without hashing paths:", digest)
    digest = sha256_file_tree(top, tree, True)
    print("With hashing paths:", digest)
