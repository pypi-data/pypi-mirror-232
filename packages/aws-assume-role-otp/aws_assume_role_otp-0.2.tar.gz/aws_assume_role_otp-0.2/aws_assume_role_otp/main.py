import typer

from aws_assume_role_otp.config import initial_config, is_first_run
from aws_assume_role_otp.credentials import (
    configure_credentials,
    credentials_configured,
    get_credentials,
    prompt_role,
)
from aws_assume_role_otp.sts import assume_selected_role

app = typer.Typer()


@app.command()
def assume_role():
    if is_first_run():
        initial_config()
    if not credentials_configured():
        configure_credentials()
    credentials = get_credentials()
    selected_role = prompt_role(credentials.roles)
    assume_selected_role(credentials, selected_role)


if __name__ == "__main__":
    app()
