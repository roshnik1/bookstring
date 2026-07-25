# BookString
BookString is an open-source reading progress tracker and social media site, think Goodreads crossed with Reddit.

## Technologies
This project uses [FastAPI](https://fastapi.tiangolo.com/) on the backend and [React](https://react.dev/) on the frontend. The python environment is managed with [uv](https://docs.astral.sh/uv/) and the typescript project is managed with [deno](https://deno.com/).

## Development
There is a lightweight [typer](https://typer.tiangolo.com/) CLI application for development use,
at `cli/`. It should be run with `uv run cli/`.

**Starting API Server**
```bash
uv run ./cli server start
```

**Starting Frontend Application**
```bash
uv run ./cli app start
```
