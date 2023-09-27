"""`/api/v4/key/distribution/nodes` endpoint."""

from typing import Optional

from aio_taginfo.api.v4 import PngResponse
from aio_taginfo.api.v4._internal import api_get_png, api_params

from aiohttp import ClientSession
from pydantic import Field, constr
from pydantic.dataclasses import dataclass


@dataclass
class _Params:
    key: constr(min_length=1, strip_whitespace=True, strict=True) = Field(repr=True, frozen=True)


async def call(key: str, session: Optional[ClientSession] = None) -> PngResponse:
    """
    Get map with distribution of this key in the database (nodes only).

    https://taginfo.openstreetmap.org/taginfo/apidoc#api_4_key_distribution_nodes

    Args:
        key: tag key
        session: request client session

    Raises:
        TagInfoError
    """
    params = api_params(_Params, key=key)
    return await api_get_png(
        path="/api/4/key/distribution/nodes",
        session=session,
        params=params,
    )


__docformat__ = "google"
