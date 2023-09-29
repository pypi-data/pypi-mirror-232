import json
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Any, Dict, Union
from uuid import UUID

from pydantic import ConfigDict, BaseModel

JsonDict = Dict[str, Any]
Floatable = Union[Decimal, int, float]


def to_camel_case(snake_str: str) -> str:
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel_case, populate_by_name=True)


def is_aware(value: Union[datetime, time]) -> bool:
    """
    Determine if a given datetime.datetime is aware.

    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def format_date(d: date) -> str:
    """
    Converts a date into a ISO 8601 (YYYY-MM-DD) format
    """
    return d.isoformat()


def format_datetime(d: datetime) -> str:
    """
    Converts a timezone aware datetime object into a UTC ISO 8601 (Zulu time) string
    """
    if not is_aware(d):
        raise Exception("Naive datetime not supported")
    return d.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class JSONEncoder(json.JSONEncoder):
    """
    Shameless copied from the Django JSON Encoder
    """

    def default(self, o: Any) -> Any:
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, (Decimal, UUID)):
            return str(o)
        else:
            return super().default(o)
