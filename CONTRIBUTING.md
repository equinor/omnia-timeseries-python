## New contributor guide

To get an overview of the project, read the [README](README.md).
Here are some resources to help you get started with open source contributions:

- [Finding ways to contribute to open source on GitHub](https://docs.github.com/en/get-started/exploring-projects-on-github/finding-ways-to-contribute-to-open-source-on-github)
- [Set up Git](https://docs.github.com/en/get-started/quickstart/set-up-git)
- [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Collaborating with pull requests](https://docs.github.com/en/github/collaborating-with-pull-requests)

### Contribution guidelines ###

* Clone the repository or Create new branch from develop
* Navigate to the project root directory
* Setup pre-commit hook
    * poetry install - Installs all dependencies, including pre-commit
    * poetry run pre-commit install - Installs pre-commit hooks
* Write code
* Write tests
* Create a PR
* Code review

### Run tests

Run tests from the project root.

1. Install dependencies:
    - `poetry install`
2. Run all tests:
    - `poetry run pytest`
3. Run a single test file (optional):
    - `poetry run pytest tests/test_api.py`
4. Run a single test case by name (optional):
    - `poetry run pytest -k "test_name"`

Before opening a PR, ensure tests pass locally.

### Release and versioning

Follow the steps below for any release that is intended for PyPI.

1. Update the package version in `pyproject.toml` under `[tool.poetry].version`.
2. Update `CHANGELOG.md` with the release notes for that exact version.
3. Merge the release PR to `main`.
4. Create and push a Git tag that exactly matches the package version prefixed with `v`.

Examples:

- `pyproject.toml` version `1.4.5` -> tag `v1.4.5`
- `pyproject.toml` version `1.4.5.post1` -> tag `v1.4.5.post1`

Versioning policy:

- Use `X.Y.Z` for normal releases (features/fixes).
- Use `X.Y.Z.postN` for packaging-only corrections where runtime behavior is unchanged.
- Do not create a release tag without first updating `pyproject.toml` to the matching version.

### Issues

#### Create a new issue

If you spot a problem with the docs, [search if an issue already exists](https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-issues-and-pull-requests#search-by-the-title-body-or-comments). If a related issue doesn't exist, you can open a new issue using a relevant [issue form](https://github.com/equinor/omnia-timeseries-python/issues/new/choose).