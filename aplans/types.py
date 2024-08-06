from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Type, TypeGuard, TypeVar

from django.http import HttpRequest

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

    from actions.models import Plan
    from users.models import User

    from .cache import PlanSpecificCache, WatchObjectCache


UserOrAnon: typing.TypeAlias = 'User | AnonymousUser'


def is_authenticated(user: UserOrAnon) -> TypeGuard[User]:
    return user.is_authenticated


class WatchRequest(HttpRequest):
    watch_cache: WatchObjectCache


class AuthenticatedWatchRequest(WatchRequest):
    user: User


class WatchAdminRequest(AuthenticatedWatchRequest):
    admin_cache: PlanSpecificCache
    def get_active_admin_plan(self) -> Plan: ...  # type: ignore[empty-body]


class WatchAPIRequest(WatchRequest):
    user: UserOrAnon
    _referer: str | None
    wildcard_domains: list[str] | None


T = TypeVar('T')


def mixin_for_base(baseclass: type[T]) -> type[T]:
    """
    Useful function to make mixins with baseclass typehint

    ```
    class ReadonlyMixin(with_typehint(BaseAdmin))):
        ...
    ```
    """
    if TYPE_CHECKING:
        return baseclass
    return object
