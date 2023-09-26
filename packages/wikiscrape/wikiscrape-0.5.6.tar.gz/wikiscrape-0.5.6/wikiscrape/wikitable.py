import re
import typing
from bs4 import BeautifulSoup

FOOTNOTE = r"(\[)(\w+|\d+)(\])"
DAGGER = "\u2020"
DOUBLE_DAGGER = "\u2021"


def remove_footnotes(text: str) -> str:
    return re.sub(
        FOOTNOTE, "", text.replace(DAGGER, "").replace(DOUBLE_DAGGER, "")
    ).strip()


class Wikitable:
    def __init__(self, table):
        self.table = table

    @property
    def headers(self) -> list[str]:
        header_cells = self.table.find_all("th")
        header_contents = [th.contents for th in header_cells]
        if not header_cells:
            return [f"col_{i+1}" for i in range(len(self.data[0]))]

        return [
            remove_footnotes(next((el.text.strip() for el in c if el.text.strip()), ""))
            for c in header_contents
        ]

    @property
    @typing.no_type_check
    def data(self) -> list[list[BeautifulSoup]]:
        de_footnoted_soup = lambda x: BeautifulSoup(
            remove_footnotes(str(x)), "html.parser"
        )

        return [
            [
                de_footnoted_soup(str(td.contents[0])).contents[0]
                if len(td.contents) == 1 and bool(str(td.contents[0]).strip())
                else de_footnoted_soup("".join(str(x) for x in td.contents))
                for td in tr.find_all("td")
            ]
            for tr in self.table.find_all("tr")
            if not tr.th
        ]

    def to_dicts(self) -> list[dict[str, BeautifulSoup]]:
        return [dict(zip(self.headers, row)) for row in self.data]
