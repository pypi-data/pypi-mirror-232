import pathlib


def get_data_dir() -> pathlib.Path:
    data_dir = pathlib.Path.home() / '.cache' / 'tree-sitter-builder'
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir


def get_repo_dir(data_dir: pathlib.Path) -> pathlib.Path:
    repo_dir = data_dir / 'repos'
    repo_dir.mkdir(parents=True, exist_ok=True)

    return repo_dir


def get_build_dir(data_dir: pathlib.Path) -> pathlib.Path:
    build_dir = data_dir / 'build'
    build_dir.mkdir(parents=True, exist_ok=True)

    return build_dir
