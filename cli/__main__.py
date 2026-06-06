import typer

from projcli import project_app
from servercli import server_app
from appcli import app_app


main_app = typer.Typer()

main_app.add_typer(
    project_app,
    name="project",
)
main_app.add_typer(
    server_app,
    name="server",
)
main_app.add_typer(
    app_app,
    name="app",
)


if __name__ == "__main__":
    main_app()