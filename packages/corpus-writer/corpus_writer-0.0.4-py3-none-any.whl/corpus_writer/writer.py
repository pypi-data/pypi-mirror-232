import datetime
import logging
import multiprocessing
import re
from collections.abc import Iterator
from pathlib import Path

import frontmatter
from citation_title import cite_title
from citation_utils import CountedCitation
from environs import Env
from statute_utils import CountedStatute, setup_local_statute_db

from .dumper import SafeDumper

env = Env()
env.read_env()

DECISIONS = Path().home().joinpath(env.str("DECISIONS_DIR"))
STATUTES = Path().home().joinpath(env.str("STATUTES_DIR"))

logging.info("Setup statutes database statute_utils matching")
setup_local_statute_db(STATUTES)

LACKING_BREAKLINE = re.compile(r"\s{2}\n(?!\n)")


def update_file(file: Path):
    logging.info(f"Start: {file.relative_to(DECISIONS)}")

    # get date string based on the path
    _, _, date_str, _ = file.parts[-4:]
    if "/opinion/" in str(file):
        _, _, date_str, _, _ = file.parts[-5:]

    # convert text from file to frontmatter
    post = frontmatter.load(file)
    text = LACKING_BREAKLINE.sub("\n\n", post.content)

    # prepare data dictionary, remove fields (if they exist) that will be updated
    updateables = ("statutes", "citations", "short")
    data = {k: post[k] for k in post.keys() if k not in updateables}

    # if title key exists, create a short title variant
    if title := data.get("title"):
        data["short"] = cite_title(title) or title[:20]

    # look for statutes based on the content and generate a statute string
    if statutes := "; ".join(
        [
            f"{c.cat.value.lower()} {c.num.lower()}: {c.mentions}"
            for c in CountedStatute.from_source(
                text=text,
                document_date=datetime.date.fromisoformat(date_str),
                context=str(file.relative_to(DECISIONS)),
            )
        ]
    ):
        data["statutes"] = statutes

    # look for citations based on the content and generate a citations string
    if citations := "; ".join([repr(c) for c in CountedCitation.from_source(text)]):
        data["citations"] = citations

    # save file with updated statutes and citations
    frontmatter.dump(post=frontmatter.Post(text, **data), fd=file, Dumper=SafeDumper)


def get_opinion_files_by_year(year: int) -> Iterator[Path]:
    return DECISIONS.glob(f"**/{str(year)}-*/**/*.md")


def update_markdown_opinion_file(file: Path):
    process = multiprocessing.Process(target=update_file, args=(file,))
    process.start()
    process.join(timeout=5)
    if process.is_alive():
        logging.error(f"Took too long: {file=}")
        process.terminate()
        process.join()
