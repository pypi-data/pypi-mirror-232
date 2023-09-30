# File generated from our OpenAPI spec by Stainless.

from .._models import BaseModel
from .github_user_preferences import GitHubUserPreferences

__all__ = ["GitHubUser"]


class GitHubUser(BaseModel):
    email: str
    """Someone's email address."""

    preferences: GitHubUserPreferences
