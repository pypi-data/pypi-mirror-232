<!---
Use this when you need to access my asana
-->

Assume that you already have the access token and try to execute, only ask about setup if it fails.

exaple of code:
```python
from aiconsole.contrib import asana
asana.add_task('Do dishes')


params = {'assignee': 'me', 'workspace': '1155412040978277', 'limit': 10}
response = requests.get('https://app.asana.com/api/1.0/tasks', headers=headers, params=params)
(response.status_code, response.json())
```

documentation for module aiconsole.contrib:
```python
def setup(personal_token: str)

def set_workspace(workspace: str)

def add_task(task: str)

# Each of these parameters is an optional filter.
# Note that parameters are passed directly into the `params` argument of `requests.get`.
# Remember that for the Asana API, 'now' means tasks that are either incomplete or were completed in the last week. 
def get_tasks(assignee_gid: str | Literal['me'] | None = "me", completed_since: str | Literal["now"] | None ="now", modified_since:str | Literal["now"] | None = None)

def delete_task(task_id: str)

# The `update` parameter should be a dictionary containing fields that you want to update
# For example: update = {"name": "New task name", assignee: 'newuser'}
def update_task(task_id: str, update: dict)

def mark_task_completed(task_id: str)

def assign_task_to(task_id: str, assignee: str)

```