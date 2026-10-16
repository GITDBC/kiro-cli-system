# Jira API Examples

Concrete `jira` library examples for operations the `jirafetcher` CLI does not cover
(JQL search, attachments, links, assignment, sprint/board queries). The library is not
declared by any project in this repository; use these only when the user's environment
provides it.

## Read a ticket

```python
import os
from jira import JIRA

jira = JIRA(server=os.environ["JIRA_URL"], token_auth=os.environ["JIRA_TOKEN"])
issue = jira.issue("PROJECT-12345")

print(issue.fields.summary)
print(issue.fields.status.name)
print(issue.fields.priority.name)
print(issue.fields.description)
print(issue.fields.assignee)
print(issue.fields.reporter)
print(issue.fields.labels)
print(issue.fields.components)
```

## Read comments

```python
for comment in jira.comments(issue):
    print(f"{comment.author.displayName} ({comment.created}): {comment.body}")
```

## Add a comment

```python
jira.add_comment(issue, "Implementation complete. MR ready for review.")
```

## Transition a ticket

```python
transitions = jira.transitions(issue)
for t in transitions:
    print(f"{t['id']}: {t['name']}")

jira.transition_issue(issue, transition="In Progress")
```

## Assign a ticket

```python
jira.assign_issue(issue, "jane.doe")
```

## Search with JQL

```python
issues = jira.search_issues(
    "project = PROJECT AND status = Open ORDER BY priority DESC",
    maxResults=50,
)
for issue in issues:
    print(f"{issue.key}: {issue.fields.summary}")
```

## Read attachments

```python
for attachment in issue.fields.attachment:
    print(f"{attachment.filename} ({attachment.size} bytes)")
    content = attachment.get()  # bytes
```

## Read issue links

```python
for link in issue.fields.issuelinks:
    if hasattr(link, "outwardIssue"):
        print(f"{link.type.outward}: {link.outwardIssue.key}")
    if hasattr(link, "inwardIssue"):
        print(f"{link.type.inward}: {link.inwardIssue.key}")
```

## Get sprint/board info

```python
boards = jira.boards(projectKeyOrID="PROJECT")
for board in boards:
    sprints = jira.sprints(board.id, state="active")
    for sprint in sprints:
        print(f"{sprint.name}: {sprint.startDate} → {sprint.endDate}")
```
