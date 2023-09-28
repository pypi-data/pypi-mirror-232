"""SystemAllMixin."""
import logging

from ..enums import Namespace
from ..http_device import HttpDeviceInfo
from .device import BaseDevice


class SystemAllMixin(BaseDevice):
    """SystemAllMixin."""
    def __init__(self, device: HttpDeviceInfo):
        """Initialize."""
        self.device = device
        super().__init__(device)

    async def async_update(self):
        """Update."""
        result = await self.async_execute_cmd(
            self.device.uuid, method="GET", namespace=Namespace.SYSTEM_ALL, payload={}
        )
        if result is None:
            return
        await super().async_handle_update(namespace=Namespace.SYSTEM_ALL, data=result)
