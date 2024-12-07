import logging
import typing

import svcs

from hbit_api.domain import commands, events

from . import unit_of_work

logger = logging.getLogger(__name__)


Message = commands.Command | events.Event


class MessageBus:
    def __init__(
        self,
        registry: svcs.Registry,
        event_handlers: events.EventHandlersConfig,
        command_handlers: commands.CommandHandlerConfig,
    ) -> None:
        self.registry = registry
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers

    def handle(self, message: Message) -> typing.Any:
        self.queue = [message]
        result = None
        with svcs.Container(self.registry) as container:
            while self.queue:
                message = self.queue.pop(0)
                match message:
                    case events.Event():
                        self.handle_event(event=message, container=container)
                    case commands.Command():
                        result = self.handle_command(message, container)

        return result

    def handle_event(self, event: events.Event, container: svcs.Container) -> None:
        uow = container.get(unit_of_work.UnitOfWork)
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug("Handling event %s with handler %s", event, handler)
                handler(event=event, services=container)
                self.queue.extend(uow.collect_new_events())
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(
        self, command: commands.Command, container: svcs.Container
    ) -> typing.Any:
        uow = container.get(unit_of_work.UnitOfWork)
        logger.debug("handling command %s", command)
        try:
            handler = self.command_handlers[type(command)]
            result = handler(cmd=command, services=container)
            self.queue.extend(uow.collect_new_events())
            return result
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
