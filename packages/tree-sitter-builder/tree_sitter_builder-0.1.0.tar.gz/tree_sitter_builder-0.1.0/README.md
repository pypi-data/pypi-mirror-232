# python-tree-sitter-builder

## Install

```bash
poetry install
ln -s $(poetry run which tree-sitter-builder) ~/.local/bin/
```

## Usage

### build

Clone specified repository and build tree-sitter language parser.

If it contains `://`, it assumes that the entire git URL has been specified. Otherwise, assume it is GitHub and clone the repository.

```bash
tree-sitter-builder build conao3/tree-sitter-sql
```

Clone into `$XDG_DATA_HOME/tree-sitter-builder/repos/*`.

If you omit the repository name, tree-sitter-builder will build all repositories.

### dist

Returns the path to builded parser shared object.

```bash
$ python-tree-sitter-builder % tree-sitter-builder dist conao3/tree-sitter-sql
/Users/conao/Library/Application Support/tree-sitter-builder/build/conao3__tree-sitter-sql.so
```

### update

Update all repositories.

```bash
tree-sitter-builder update
```

### list

List all repositories.

```bash
tree-sitter-builder list
```

### remove

Remove specified repository.

```bash
tree-sitter-builder remove conao3/tree-sitter-sql
```

### clean

Remove all build files.

```bash
tree-sitter-builder clean
```
