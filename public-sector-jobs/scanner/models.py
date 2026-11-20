from dataclasses import dataclass, field, asdict


@dataclass
class Job:
    source: str
    title: str
    organisation: str
    url: str
    location: str = ""
    salary: str = ""
    posted: str = ""      # ISO date
    closing: str = ""     # human readable or ISO
    extra: dict = field(default_factory=dict)

    @property
    def key(self):
        return self.url.split("?")[0]

    def to_dict(self):
        return asdict(self)


@dataclass
class PeopleMove:
    source: str
    headline: str
    url: str
    published: str
    summary: str = ""

    def to_dict(self):
        return asdict(self)
