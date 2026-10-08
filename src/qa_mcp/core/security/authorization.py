from __future__ import annotations

from collections.abc import Iterable

from qa_mcp.core.security.actor import Actor, current_actor


class AuthorizationError(PermissionError):
    """Raised when an actor does not hold the required project access."""


class ProjectAuthorization:
    def __init__(self, repository, global_admin_subjects: Iterable[str] = ()):
        self.repository = repository
        self.global_admin_subjects = frozenset(global_admin_subjects)

    def is_global_admin(self, actor: Actor | None = None) -> bool:
        actor = actor or current_actor()
        return actor.local_operator or actor.subject in self.global_admin_subjects

    def require_project(self, project_id: str, actor: Actor | None = None) -> None:
        actor = actor or current_actor()
        if not self.repository.project_exists(project_id):
            raise ValueError(f"Project not found: {project_id}")
        if self.is_global_admin(actor):
            return
        if not self.repository.is_project_member(project_id, actor.subject):
            raise AuthorizationError("Project access denied")

    def visible_project_ids(self, actor: Actor | None = None) -> list[str] | None:
        actor = actor or current_actor()
        if self.is_global_admin(actor):
            return None
        return self.repository.list_project_ids(actor.subject)

    def grant_member(self, project_id: str, actor_id: str, actor: Actor | None = None) -> None:
        actor = actor or current_actor()
        if not self.is_global_admin(actor):
            raise AuthorizationError("Project administration denied")
        self.require_project(project_id, actor)
        self.repository.grant_project_member(project_id, actor_id)
