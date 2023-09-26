# corpus-writer

![Github CI](https://github.com/justmars/corpus-writer/actions/workflows/main.yml/badge.svg)

With a pre-existing markdown file in frontmatter format from a decisions directory, update the `DecisionFile`
to reflect discovered statutes and citations.

The _decisions_ / _statutes_ directories needs to be configured via an `.env` file, see `just dumpenv` for an example.

## Development

See [documentation](https://justmars.github.io/corpus-writer).

1. Run `poetry install`
2. Run `poetry shell`
3. Run `pytest`
