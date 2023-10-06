from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING

from trame.decorators.klass import can_be_decorated, logger

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


@dataclass
class AppExtend:
    app: App

    def __post_init__(self):
        prefix = ""
        # Look for method decorator
        for k in inspect.getmembers(self.__class__, can_be_decorated):
            fn = getattr(self, k[0])

            # Handle @state.change
            if "_trame_state_change" in fn.__dict__:
                state_change_names = fn.__dict__["_trame_state_change"]
                logger.debug(
                    f"state.change({[f'{prefix}{v}' for v in state_change_names]})({k[0]})"
                )
                self.app.server.state.change(*[f"{prefix}{v}" for v in state_change_names])(fn)

            # Handle @trigger
            if "_trame_trigger_names" in fn.__dict__:
                trigger_names = fn.__dict__["_trame_trigger_names"]
                for trigger_name in trigger_names:
                    logger.debug(f"trigger({trigger_name})({k[0]})")
                    self.app.server.trigger(f"{trigger_name}")(fn)
                    if prefix:
                        logger.debug(f"trigger({prefix}{trigger_name})({k[0]})")
                        self.app.server.trigger(f"{prefix}{trigger_name}")(fn)