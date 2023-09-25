from __future__ import annotations

from typing import TYPE_CHECKING

from likeinterface.enums import Services
from likeinterface.methods.base import Method, Request
from likeinterface.types import User

if TYPE_CHECKING:
    from likeinterface.interface import Interface


class GetUser(Method[User]):
    """
    Use this method to get information about any user.

    Parameters
      Name       | Type    | Required | Description

      1. user_id | Integer | Yes      | User ID in the system

    Result
      :class:`likeinterface.types.user.User`
    """

    __service_name__ = Services.AUTH
    __name__ = "getUser"
    __returning__ = User

    user_id: int

    def request(self, interface: Interface) -> Request:
        return Request(method=self.__name__, data=self.model_dump())
