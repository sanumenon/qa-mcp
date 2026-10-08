from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    """A verified application actor or trusted local operator."""

    subject: str
    email: str | None = None
    authenticated: bool = True
    local_operator: bool = False


LOCAL_OPERATOR = Actor(
    subject="local-operator",
    email=None,
    authenticated=True,
    local_operator=True,
)

_current_actor: ContextVar[Actor] = ContextVar(
    "qa_mcp_current_actor",
    default=LOCAL_OPERATOR,
)


def current_actor() -> Actor:
    return _current_actor.get()


def set_current_actor(actor: Actor):
    return _current_actor.set(actor)


def reset_current_actor(token) -> None:
    _current_actor.reset(token)

