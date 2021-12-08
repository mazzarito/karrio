"""Purplship API Gateway definition modules."""

import attr
import logging
import warnings
from typing import Callable, Union, List

from purplship.api.proxy import Proxy
from purplship.api.mapper import Mapper
from purplship.core import Settings
from purplship.core.models import Message
from purplship.core.errors import ShippingSDKError
from purplship.references import import_extensions, detect_capabilities

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class Gateway:
    """The carrier connection instance"""

    mapper: Mapper
    proxy: Proxy
    settings: Settings

    @property
    def capabilities(self) -> List[str]:
        return detect_capabilities(self.proxy.__class__)

    def check(self, request: str, origin_country_code: str = None):
        messages = []

        if request not in self.capabilities:
            messages.append(
                Message(
                    carrier_id=self.settings.carrier_id,
                    carrier_name=self.settings.carrier_name,
                    code="SHIPPING_SDK_NON_SUPPORTED_ERROR",
                    message="this operation is not supported.",
                )
            )

        if (
            any(origin_country_code or "")
            and any(self.settings.account_country_code or "")
            and (origin_country_code != self.settings.account_country_code)
        ):
            messages.append(
                Message(
                    carrier_id=self.settings.carrier_id,
                    carrier_name=self.settings.carrier_name,
                    code="SHIPPING_SDK_ORIGIN_NOT_SERVICED_ERROR",
                    message="this account cannot ship from origin {}".format(
                        origin_country_code
                    ),
                )
            )

        return messages

    @property
    def features(self) -> List[str]:
        warnings.warn(
            "features is deprecated. Use capabilities instead",
            category=DeprecationWarning,
        )
        return self.capabilities


@attr.s(auto_attribs=True)
class ICreate:
    """A gateway initializer type class"""

    initializer: Callable[[Union[Settings, dict]], Gateway]

    def create(self, settings: Union[Settings, dict]) -> Gateway:
        """A gateway factory with a fluent API interface.

        Args:
            settings (Union[Settings, dict]): carrier connection configuration

        Returns:
            Gateway: The carrier connection instance
        """
        return self.initializer(settings)


class GatewayInitializer:
    """Gateway initializer helper"""

    __instance: "GatewayInitializer" = None

    def __init__(self):
        if GatewayInitializer.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GatewayInitializer.__instance = self

    def __getitem__(self, key: str) -> ICreate:
        """Map a provider's name to return a way to initialize it

        Args:
            key (str): a provider's name

        Returns:
            ICreate: the corresponding provider's Gateway initializer
        """

        try:
            provider = self.providers[key]

            def initializer(settings: Union[Settings, dict]) -> Gateway:
                """Initialize a provider gateway with the required settings

                Args:
                    settings (Union[Settings, dict]): the provider settings

                Returns:
                    Gateway: a gateway instance
                """
                try:
                    settings_value: Settings = (
                        provider.Settings(**settings)
                        if isinstance(settings, dict)
                        else settings
                    )
                    return Gateway(
                        settings=settings_value,
                        proxy=provider.Proxy(settings_value),
                        mapper=provider.Mapper(settings_value),
                    )
                except Exception as er:
                    raise ShippingSDKError(f"Failed to setup provider '{key}'") from er

            return ICreate(initializer)
        except KeyError as e:
            raise ShippingSDKError(f"Unknown provider '{key}'") from e

    @property
    def providers(self):
        return import_extensions()

    @staticmethod
    def get_instance() -> "GatewayInitializer":
        """Return the singleton instance of the GatewayInitializer"""

        if GatewayInitializer.__instance is None:
            GatewayInitializer()
        return GatewayInitializer.__instance


nl = "\n    "
logger.info(
    f"""
Purplship default gateway mapper initialized.
"""
)