from .wikiobject import Wikiobject


class Coordinates(Wikiobject):
    _html_tag = "span"
    _identifier = {"class": "geo-dms"}

    @property
    def latitude(self):
        return (
            self.value.find("span", {"class": "latitude"}).text if self.value else None
        )

    @property
    def longitude(self):
        return (
            self.value.find("span", {"class": "longitude"}).text if self.value else None
        )
