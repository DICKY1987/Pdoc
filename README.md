# Pdoc Economic Specifications

This repository stores economic specification documents and a simple linter to keep them consistent.

## Specifications

All specification files live in the [`pdoc/`](pdoc/) directory.

## Linting

Use `econ_doc_lint.py` to check a specification file for matching block markers, valid cross references, and required metadata fields:

```bash
python pdoc/econ_doc_lint_2025-09-05_21-17-35.py pdoc/econ_spec_standardized.md
```

Replace the second argument with any spec you want to validate. The script prints `OK: Lint passed` on success or a list of problems to fix.

## Contributing

1. Fork the repository and create a topic branch.
2. Add or modify spec documents under `pdoc/`.
3. Run `econ_doc_lint.py` on your changes before committing.
4. Submit a pull request describing your updates.

