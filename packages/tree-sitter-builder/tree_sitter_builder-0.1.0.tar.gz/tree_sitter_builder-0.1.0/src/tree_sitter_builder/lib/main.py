import logging
import pathlib

import tree_sitter

from .. import subr

logger = logging.getLogger(__name__)

def build(repository: str, repo_dir: pathlib.Path, build_dir: pathlib.Path):
    clone_dir_name = subr.git.get_repo_name(repository)
    target_file = build_dir / (clone_dir_name + ".so")

    logger.info(f'Build tree-sitter module: {str(target_file)}')
    target_file.unlink(missing_ok=True)
    tree_sitter.Language.build_library(
        str(target_file),
        [str(repo_dir / clone_dir_name)]
    )
