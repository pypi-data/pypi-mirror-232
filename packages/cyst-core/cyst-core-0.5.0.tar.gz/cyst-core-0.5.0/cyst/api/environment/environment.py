from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List

from cyst.api.configuration.configuration import ConfigItem
from cyst.api.environment.configuration import EnvironmentConfiguration
from cyst.api.environment.control import EnvironmentControl
from cyst.api.environment.messaging import EnvironmentMessaging
from cyst.api.environment.resources import EnvironmentResources
from cyst.api.environment.policy import EnvironmentPolicy


class EnvironmentMode(Enum):
    SIMULATION = auto()
    EMULATION_CRYTON = auto()


class Environment(ABC):
    """
    The Environment provides a highest-level interface to controlling the simulation. It consists of a number of
    lower-level interfaces that provide a specific functionality.
    """
    @property
    @abstractmethod
    def configuration(self) -> EnvironmentConfiguration:
        """
        This interface is a collection of configuration interfaces for the environment, that are split according to
        their general functionality.

        :rtype: EnvironmentConfiguration
        """

    @property
    @abstractmethod
    def control(self) -> EnvironmentControl:
        """
        This interface provides mechanisms to control the execution of actions within the simulation environment.

        :rtype: EnvironmentControl
        """

    @property
    @abstractmethod
    def messaging(self) -> EnvironmentMessaging:
        """
        This interface enables creating and sending of messages within simulation.

        :rtype: EnvironmentMessaging
        """

    @property
    @abstractmethod
    def policy(self) -> EnvironmentPolicy:
        """
        This environment enables handling of authentication and authorization.

        Warning:
            This interface will be gradually phased off in favor of a new auth framework.

        :rtype: EnvironmentPolicy
        """

    @property
    @abstractmethod
    def resources(self) -> EnvironmentResources:
        """
        This interface gives access to resources, such as actions or exploits.

        :rtype: EnvironmentResources
        """

    @abstractmethod
    def configure(self, *config_item: ConfigItem) -> 'Environment':
        """
        Configures the environment, according to provided configuration items. This function can be called repeatedly,
        however, each subsequent call replaces the previous configuration. Therefore, a configuration must be done
        at once and every later change in the environment setup must be done through the
        :class:`cyst.api.environment.configuration.EnvironmentConfiguration` interface.

        :param config_item: One or more configuration items. The number of items can be arbitrary and it is not
            order-dependent.
        :type config_item: ConfigItem

        :return: The configured environment. Used this way for the shorthand form:

        .. code-block:: python

            e = Environment.create().configure(*config)

        """

    @classmethod
    def create(cls, mode: EnvironmentMode = EnvironmentMode.SIMULATION) -> 'Environment':
        """
        Creates a new instance of the environment. A program using CYST can use multiple environments, however, each
        simulation run happens only in the context of one environment.

        :return: An environment instance.
        """
        import cyst.core.environment.environment
        return cyst.core.environment.environment.create_environment()
