# corpus-writer

![Github CI](https://github.com/justmars/corpus-writer/actions/workflows/main.yml/badge.svg)

Update pre-existing opinion file (in markdown front-matter) with statutes, citations, short title.

The _decisions_ / _statutes_ directories needs to be configured via an `.env` file, see `just dumpenv` for an

## Errors

1. Took too long: file=PosixPath('/Users/mv/code/corpus-decisions/am/97-9-282-rtc/1998-04-22/main-123.md')

## Development

See [documentation](https://justmars.github.io/corpus-writer).

1. Run `poetry install`
2. Run `poetry shell`
3. Run `pytest`
