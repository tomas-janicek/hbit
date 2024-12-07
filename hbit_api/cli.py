import svcs
import typer
from pydantic import SecretStr

from hbit_api.bootstrap import bootstrap
from hbit_api.core.config import settings
from hbit_api.domain import commands
from hbit_api.service_layer import messagebus

cli = typer.Typer()


@cli.command(name="init_db_data")
def init_db_data() -> None:
    registry = svcs.Registry()
    bootstrap(registry)
    services = svcs.Container(registry)

    bus = services.get(messagebus.MessageBus)

    create_user = commands.CreateUser(
        email=settings.FIRST_SUPERUSER,
        name="Super User",
        password=SecretStr(settings.FIRST_SUPERUSER_PASSWORD),
        is_superuser=True,
    )
    bus.handle(create_user)


@cli.command(name="remove")
def remove() -> None: ...


if __name__ == "__main__":
    cli()
