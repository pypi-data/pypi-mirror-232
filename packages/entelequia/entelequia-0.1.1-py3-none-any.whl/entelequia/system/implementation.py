from __future__ import annotations

from abc import ABC, abstractmethod

from attrs import define, field


class SystemState(ABC):
    def __init__(self, system: SystemImplementation):
        self.system: SystemImplementation = system

    @abstractmethod
    def start_up(self) -> None:
        pass

    @abstractmethod
    def shut_down(self) -> None:
        pass

    def is_started(self) -> bool:
        return False

    def is_stopped(self) -> bool:
        return False


class SystemStopped(SystemState):
    def is_stopped(self) -> bool:
        return True

    def start_up(self) -> None:
        self.system.start_up_when_stopped()

    def shut_down(self) -> None:
        raise AssertionError(f"{self.system.name} is already stopped.")


class SystemStarted(SystemState):
    def is_started(self) -> bool:
        return True

    def start_up(self) -> None:
        raise AssertionError(f"{self.system.name} is already started.")

    def shut_down(self) -> None:
        self.system.shut_down_when_started()


@define
class SystemImplementation(ABC):
    state: SystemState = field(init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        self.state: SystemState = SystemStopped(self)

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __repr__(self) -> str:
        return self.name

    def is_started(self) -> bool:
        return self.state.is_started()

    def is_stopped(self) -> bool:
        return self.state.is_stopped()

    @abstractmethod
    def start_up_when_stopped(self) -> None:
        pass

    @abstractmethod
    def shut_down_when_started(self) -> None:
        pass

    def start_up(self) -> None:
        self.state.start_up()
        self.state = SystemStarted(self)

    def shut_down(self) -> None:
        self.state.shut_down()
        self.state = SystemStopped(self)


@define(repr=False)
class SubsystemImplementation(SystemImplementation):
    def __init__(self) -> None:
        super().__init__()
        self.be_orphan()
        self.reset_dependencies()

    def start_up_when_stopped(self) -> None:
        self.resolve_dependencies()
        super().start_up_when_stopped()

    def shut_down_when_started(self) -> None:
        self.reset_dependencies()
        super().shut_down_when_started()

    def be_orphan(self) -> None:
        pass

    def reset_dependencies(self) -> None:
        pass

    def resolve_dependencies(self) -> None:
        pass
