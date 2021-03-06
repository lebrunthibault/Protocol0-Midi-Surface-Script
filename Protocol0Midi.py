from types import MethodType

from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from _Framework.Util import find_if
from typing import Any, Tuple

from protocol0.application.Protocol0 import Protocol0
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.midi.MidiBytesReceivedEvent import MidiBytesReceivedEvent
from protocol0.shared.logging.LogLevelEnum import LogLevelEnum


class Protocol0Midi(ControlSurface):
    """
    This is needed because we cannot select multiple input ports in Live and windows MIDI ports are single client.
    So we send input to a loopback port connected to this small script and route it back to the main script.
    Alternate solution is more cumbersome: Merge midi ports with something like Bome

    This expects the Protocol0 lint to be in the Remote scripts (will not even appear in the list otherwise)
    And will log an error if the Protocol0 script is not used as a Control Surface
    """

    def __init__(self, c_instance=None):
        # type: (Any, bool) -> None
        # hide initializing message
        log_message = self.log_message
        self.log_message = lambda a: True
        super(Protocol0Midi, self).__init__(c_instance=c_instance)
        self.log_message = log_message
        # stop log duplication
        self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa
        self.main_p0_script = find_if(lambda s: isinstance(s, Protocol0), get_control_surfaces())  # type: Protocol0

        self._logger = LoggerService()
        if self.main_p0_script is None:
            self._logger.log("Error: couldn't find main Protocol0 script", level=LogLevelEnum.ERROR)
            return
        self._logger.log("Notifying Protocol0Midi up", level=LogLevelEnum.DEBUG)
        Backend.client().notify_protocol0_midi_up()

    def receive_midi(self, midi_bytes):
        # type: (Tuple) -> None
        DomainEventBus.emit(MidiBytesReceivedEvent(midi_bytes))
