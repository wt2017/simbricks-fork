# Copyright 2021 Max Planck Institute for Software Systems, and
# National University of Singapore
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import annotations

import abc
import datetime
import enum
from typing import TypeVar, Generic, Literal, Annotated, Any, Type, Callable
from pydantic import BaseModel, TypeAdapter, Field, field_serializer


class ApiNamespace(BaseModel):
    id: int | None = None
    parent_id: int | None = None
    name: str
    base_path: str | None = None


ApiNamespaceList_A = TypeAdapter(list[ApiNamespace])


class ApiSystem(BaseModel):
    id: int | None = None
    sb_json: str | dict | None = None
    namespace_id: int | None = None


ApiSystemList_A = TypeAdapter(list[ApiSystem])


class ApiSystemQuery(BaseModel):
    namespace_id: int | None = None
    limit: int | None = None


class ApiSimulation(BaseModel):
    id: int | None = None
    namespace_id: int = None
    system_id: int = None
    sb_json: str | dict | None = None


ApiSimulationList_A = TypeAdapter(list[ApiSimulation])


class ApiSimulationQuery(BaseModel):
    id: int | None = None
    namespace_id: int = None
    system_id: int = None
    limit: int | None = None


class ApiFragment(BaseModel):
    id: int | None = None
    object_id: int | None = None
    instantiation_id: int | None = None
    cores_required: int | None = None
    memory_required: int | None = None
    runner_tags: list[str] | None = None
    fragment_executor_tag: str | None = None


class ApiFragmentQuery(BaseModel):
    id: int | None = None
    instantiation_id: int | None = None
    limit: int | None = None


class ApiInstantiation(BaseModel):
    id: int | None = None
    simulation_id: int | None = None
    sb_json: str | dict | None = None
    fragments: list[ApiFragment] | None = None


ApiInstantiationList_A = TypeAdapter(list[ApiInstantiation])


class ApiInstantiationQuery(BaseModel):
    id: int | None = None
    simulation_id: int | None = None
    fragments: list[ApiFragmentQuery] = []
    limit: int | None = None


class RunState(str, enum.Enum):
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            ranking = {
                RunState.SPAWNED: 1,
                RunState.PENDING: 2,
                RunState.RUNNING: 3,
                RunState.COMPLETED: 4,
                RunState.ERROR: 5,
                RunState.CANCELLED: 6,
            }
            return ranking[self] > ranking[other]
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self > other or self == other
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return not (self >= other)
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return not (self > other)
        return NotImplemented

    SPAWNED = "spawned"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class ApiRun(BaseModel):
    id: int | None = None
    namespace_id: int | None = None
    instantiation_id: int | None = None
    state: RunState | None = None
    output: str | None = None


ApiRunList_A = TypeAdapter(list[ApiRun])


class ApiRunQuery(BaseModel):
    id: int | None = None
    namespace_id: int | None = None
    instantiation_id: int | None = None
    state: RunState | None = None
    limit: int | None = None


class ApiRunFragment(BaseModel):
    id: int | None = None
    run_id: int | None = None
    runner_id: int | None = None
    fragment: ApiFragment | None = None
    state: RunState | None = None
    output_artifact_exists: bool | None = None


class ApiRunFragmentQuery(BaseModel):
    id: int | None = None
    run_id: int | None = None
    runner_id: int | None = None
    fragment_id: int | None = None
    state: RunState | None = None
    limit: int | None = None


class ApiResourceGroup(BaseModel):
    id: int | None = None
    label: str | None = None
    namespace_id: int | None = None
    available_cores: int | None = None
    available_memory: int | None = None
    cores_left: int | None = None
    memory_left: int | None = None


ApiResourceGroupList_A = TypeAdapter(list[ApiResourceGroup])


class ApiRunnerTag(BaseModel):
    label: str


class RunnerStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    OFFLINE = "OFFLINE"


class ApiRunner(BaseModel):
    id: int | None = None
    label: str | None = None
    namespace_id: int | None = None
    resource_group_id: int | None = None
    status: RunnerStatus | None = None
    tags: list[ApiRunnerTag] = []
    plugin_tags: list[ApiRunnerTag] = []


ApiRunnerList_A = TypeAdapter(list[ApiRunner])


class RunnerEventAction(str, enum.Enum):
    KILL = "kill"
    HEARTBEAT = "heartbeat"
    SIMULATION_STATUS = "simulation_status"
    START_RUN = "start_run"


# TODO: Remove
class ApiRunnerEventQuery(BaseModel):
    action: None = None
    run_id: int | None = None
    event_status: None = None
    runner_id: int | None = None
    limit: int | None = None


class RunComponentState(str, enum.Enum):
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            ranking = {
                RunComponentState.UNKNOWN: 1,
                RunComponentState.PREPARING: 2,
                RunComponentState.STARTING: 3,
                RunComponentState.RUNNING: 4,
                RunComponentState.TERMINATED: 5,
            }
            return ranking[self] > ranking[other]
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self > other or self == other
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return not (self >= other)
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return not (self > other)
        return NotImplemented

    UNKNOWN = "unknown"
    PREPARING = "preparing"
    STARTING = "starting"
    RUNNING = "running"
    TERMINATED = "terminated"


class ApiSimulatorState(BaseModel):
    run_id: int
    simulator_id: int
    simulator_name: str | None = None
    command: str | None = None
    state: RunComponentState | None = None


class ApiProxyState(BaseModel):
    run_id: int
    proxy_id: int
    proxy_name: str | None = None
    ip: str | None = None
    port: int | None = None
    command: str | None = None
    state: RunComponentState | None = None


class ApiConsoleOutputLine(BaseModel):
    id: int | None = None
    produced_at: datetime.datetime
    output: str
    is_stderr: bool


class ApiRunSimulatorOutput(BaseModel):
    run_id: int
    simulator_id: int
    output_lines: list[ApiConsoleOutputLine] = []


class ApiRunProxyOutput(BaseModel):
    run_id: int
    proxy_id: int
    output_lines: list[ApiConsoleOutputLine] = []


class ApiRunComponent(BaseModel):
    name: str
    commands: dict[str, list[ApiConsoleOutputLine]] = {}


class ApiRunOutput(BaseModel):
    run_id: int
    simulators: dict[int, ApiRunComponent] = {}
    proxies: dict[int, ApiRunComponent] = {}


class ApiRunOutputFilter(BaseModel):
    simulator_seen_until_line_id: int | None = None
    proxy_seen_until_line_id: int | None = None


class ApiOrgInvite(BaseModel):
    email: str
    first_name: str
    last_name: str


class ApiOrgGuestCred(BaseModel):
    email: str


class ApiOrgGuestMagicLinkResp(BaseModel):
    magic_link: str


""" ############################################################################
Schema objects used in SimBricks 'Generic Event Handling Interface':
"""  ############################################################################

EVENT_REGISTRY: dict[str, Type[BaseModel]] = {}


class Event(BaseModel, abc.ABC):
    event_discriminator: str = Field(init=False)
    """
    The event event_discriminator, is be used to reconstruct pydantic model.
    See pydantics discriminated union.
    """
    id: int | None
    """
    Generic identifier for an event. Subclasses should OVEWRITE this explicitly IN CASE the id is OPTIONAL.
    """
    runner_id: int
    """
    Generic identifier for an event. Subclasses should OVEWRITE this explicitly IN CASE the id is OPTIONAL.
    """
    acknowledged: bool = False
    """
    The status of this specific event.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        event_discriminator = cls.__name__

        cls.model_fields["event_discriminator"].annotation = Literal[event_discriminator]
        cls.model_fields["event_discriminator"].default = event_discriminator

        assert event_discriminator not in EVENT_REGISTRY
        EVENT_REGISTRY[event_discriminator] = cls


class Ack(Event):
    to_ack_id: int


class RunnerHeartbeat(Event):
    pass


class RunnerStateChange(Event):
    old_status: RunnerStatus = RunnerStatus.HEALTHY
    new_status: RunnerStatus = RunnerStatus.HEALTHY


"""
Utils useful for validation, parsing etc. 
"""


def parse_event(event: dict) -> Event:
    disc = event.get("event_discriminator", None)
    if not disc:
        raise ValueError(f"{event} does not have key 'event_discriminator'")
    event_cls = EVENT_REGISTRY.get(disc, None)
    if not event_cls:
        raise ValueError(f"unkonw event class {event_cls}")
    return event_cls.model_validate(event)


def parse_events(events: list[dict]) -> list[Event]:
    res = []
    for event in events:
        res.append(parse_event(event))
    return res


def dump_events(events: list[Event]) -> list[dict[str, any]]:
    return [m.model_dump() for m in events]


Model_Class_T = TypeVar("Model_Class_T")


def validate_list_type(
    model_list: list[Event], model_class: Type[Model_Class_T]
) -> list[Model_Class_T]:
    adapter = TypeAdapter(list[Model_Class_T])
    validated_model_list = adapter.validate_python(model_list)
    return validated_model_list


Source_Class_T = TypeVar("Source_Class_T")
Target_Class_T = TypeVar("Target_Class_T")


def convert_validate_type(
    source: list[BaseModel], target: Type[Target_Class_T]
) -> list[Target_Class_T]:
    assert isinstance(target, type) and issubclass(target, BaseModel)
    converted = []
    for mod in source:
        dump = mod.model_dump()
        conv = target.model_validate(dump)
        converted.append(conv)
    return converted


def convert_validate_factory(
    source: list[Source_Class_T], factory: Callable[[Source_Class_T], Target_Class_T]
) -> list[Target_Class_T]:
    converted = []
    for mod in source:
        assert isinstance(mod, BaseModel)
        conv = factory(mod)
        converted.append(conv)
    return converted


# import json

# events = [
#     RunnerStateChange(id=None, runner_id=234),
#     RunnerHeartbeat(id=23, runner_id=234),
#     Ack(id=256, runner_id=2234, to_ack_id=1753),
# ]

# dumped = json.dumps(dump_events(events))

# loaded = json.loads(dumped)

# events = parse_events(loaded)
# print(events)
