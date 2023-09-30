<h1 align="center">AI Console</h1>

## Running Your AI Console

In order to run your own AI Console:

1. CD into the project folder `/ai-console`
2. Install dependencies `poetry install` and `cd web && yarn`
3. In two distinct terminal windows run: `poetry run backend` and `cd web && yarn dev`

Optionally you can run `poetry run aiconsole` which will spawn two servers, but it's less ideal for development as it's often benefitial to restart just one.

Requires OPENAI_API_KEY env variable to be set.

## Publishing process

poetry run aiconsole
poetry publish --username _token_ --password ...

## Manuals

Create .md files in ./manuals directory in the following format:


```md
<!---
Description of when this manual should be used?
-->

Actual content of a manual
```

Files are monitored and automatically loaded, then used as context. You can keep there API manuals, login information, prompts and other contextual information.

You can see examples of manuals i ./preset/manuals directory
