# Shipped in Open Forms
from openforms.contrib.hal_client import HALClient
from openforms.pre_requests.clients import PreRequestMixin
from zgw_consumers_ext.api_client import ServiceClientFactory

from .models import HaalCentraalHRConfig


class NoServiceConfigured(RuntimeError):
    pass


def get_client(**kwargs) -> "Client":
    config = HaalCentraalHRConfig.get_solo()
    assert isinstance(config, HaalCentraalHRConfig)
    if not (service := config.service):
        raise NoServiceConfigured("No service configured!")
    service_client_factory = ServiceClientFactory(service)
    return Client.configure_from(service_client_factory, **kwargs)


class Client(PreRequestMixin, HALClient):
    pass
