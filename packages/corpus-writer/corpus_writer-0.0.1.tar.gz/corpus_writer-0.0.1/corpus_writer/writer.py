import datetime
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import frontmatter
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


@dataclass
class DecisionFile:
    file: Path

    def __post_init__(self):
        logging.info(f"Start: {self.file.relative_to(DECISIONS)}")

        # convert text from file to frontmatter
        self.post = frontmatter.load(self.file)

        # remove existing statutes / citations from file
        self.data = {
            k: self.post[k]
            for k in self.post.keys()
            if k not in ("statutes", "citations")  # remove
        }

        # look for statutes based on the content and generate a statute string
        raw_statutes = list(
            CountedStatute.from_source(
                text=self.post.content,
                document_date=self.extract_date_from_file(self.file),
                context=str(self.file.relative_to(DECISIONS)),
            )
        )
        if raw_statutes:
            self.data["statutes"] = "; ".join(
                [
                    f"{c.cat.value.lower()} {c.num.lower()}: {c.mentions}"
                    for c in raw_statutes
                ]
            )

        # look for citations based on the content and generate a citations string
        cites = CountedCitation.from_source(self.post.content)
        if citations := "; ".join([repr(c) for c in cites]):
            self.data["citations"] = citations

        # save file with updated statutes and citations
        content = LACKING_BREAKLINE.sub("\n\n", self.post.content)
        frontmatter.dump(
            post=frontmatter.Post(content, **self.data),
            fd=self.file,
            Dumper=SafeDumper,
        )

    @staticmethod
    def extract_date_from_file(path: Path) -> datetime.date:
        _, _, date_str, _ = path.parts[-4:]
        if "/opinion/" in str(path):
            _, _, date_str, _, _ = path.parts[-5:]
        return datetime.date.fromisoformat(date_str)

    @staticmethod
    def filter_decisions_by_year(year: str):
        return DECISIONS.glob(f"**/{year}-*/**/*.md")

    @staticmethod
    def target_file(glob_match: str):
        return next(DECISIONS.glob(glob_match))
