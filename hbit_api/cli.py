import logging

import svcs
import typer
from pydantic import SecretStr

from hbit_api.bootstrap import bootstrap
from hbit_api.core.config import settings
from hbit_api.domain import commands
from hbit_api.service_layer import messagebus

_log = logging.getLogger(__name__)

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


@cli.command(name="healthy")
def healthy() -> None:
    registry = svcs.Registry()
    bootstrap(registry)
    services = svcs.Container(registry)

    for svc in services.get_pings():
        try:
            svc.ping()
            _log.info("Service %s is healthy!", svc.name)
        except Exception as e:
            _log.warning("Service %s is NOT healthy because %s", svc.name, str(e))


if __name__ == "__main__":
    cli()
