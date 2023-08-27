"""
Base release worker module
"""

from abc import ABC, abstractmethod
from typing import Optional
from config import Config
from core.nova_component_release import NovaComponentRelease
from core.cvs import GitCloudService
from core.nova_component import NovaComponent
from core.nova_release import NovaRelease
from core.nova_status import Status


class ReleaseWorker(ABC):
    """
    Base class for release workers.
    """

    _defult_text_editor = "vim"

    def __init__(self, release: NovaRelease, config: Config) -> None:
        self._release = release
        self._text_editor = (
            config.data["textEditor"] or self._defult_text_editor
        )

    @property
    @abstractmethod
    def git_cloud(self) -> GitCloudService:
        """
        Returns the Git cloud service the worker is designed for.
        """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.git_cloud is None:
            raise ValueError(
                f"Git cloud service is not specified for {cls.__name__}"
            )

    @abstractmethod
    def release_component(
        self, component: NovaComponent
    ) -> Optional[NovaComponentRelease]:
        if component is None:
            raise ValueError("Component is not specified")

        if component.repo is None:
            raise ValueError(
                f"Component [{component.name}] does not have repository"
            )

        if component.repo.git_cloud != self.git_cloud:
            raise ValueError(
                f"Component [{component.name}] not hosted on {self.git_cloud}"
            )

        if component.status == Status.DONE:
            raise ValueError(
                f"Component [{component.name}] is already released"
            )

        if component.status != Status.READY_FOR_RELEASE:
            raise ValueError(
                f"Component [{component.name}] is not ready for release"
            )
