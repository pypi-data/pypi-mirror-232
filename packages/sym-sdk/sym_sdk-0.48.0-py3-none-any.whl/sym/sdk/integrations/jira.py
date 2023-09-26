"""Helpers for interacting with the Jira API within the Sym SDK."""


from typing import List, Optional

from sym.sdk.exceptions import JiraError  # noqa


def search_issues(
    jql: str,
    fields: Optional[List[str]] = None,
    expand: Optional[List[str]] = None,
) -> List[dict]:
    """Returns a list of issues matching the given JQL query.

    See Jira's API
    `docs <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-postt>`_ for details.

    Args:
        jql: A non-empty JQL expression.
        fields: A list of fields to return for each issue. Use it to retrieve a subset of fields.
        expand: An optional list of strings indicating what additional information about issues to include in the response.

    Returns:
        A list of dictionaries representing Jira issues.

    Raises:
        :class:`~sym.sdk.exceptions.jira.JiraError`: If the JQL expression is empty.
    """


def add_comment_to_issue(
    issue_id_or_key: str,
    comment: str,
    expand: Optional[List[str]] = None,
) -> None:
    """Adds a comment to a Jira issue.

    See Jira's API docs
    `here <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post>`_ for details.

    Args:
        issue_id_or_key: The ID or key of the issue.
        comment: A string to be added as a comment to the Jira issue.
        expand: An optional list of strings indicating what additional information about issues to include in the response.

    Raises:
        :class:`~sym.sdk.exceptions.jira.JiraError`: If the issue does not exist.
    """
