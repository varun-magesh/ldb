import asyncio
from dbus_next.aio import MessageBus
from dbus_next import Variant

class Zathura:
    loop = asyncio.get_event_loop()
    interface = None

    def __init__(self, pid):
        self.pid = pid
        Zathura.loop.run_until_complete(self._async_init(),)

    async def _async_init(self):
        self.bus = await MessageBus().connect()
        self.introspection = await self.bus.introspect(f'org.pwmt.zathura.PID-{self.pid}', '/org/pwmt/zathura')
        self.proxy_object = self.bus.get_proxy_object(f'org.pwmt.zathura.PID-{self.pid}', \
                                            '/org/pwmt/zathura', \
                                            self.introspection)
        self.interface = self.proxy_object.get_interface('org.pwmt.zathura')

    async def async_get_page(self):
        return await self.interface.get_pagenumber()

    async def async_get_page(self, page):
        return await self.interface.call_goto_page(page)

    def get_page(self):
        return Zathura.loop.run_until_complete(self.async_get_page(),)

    def set_page(self, page):
        return Zathura.loop.run_until_complete(self.async_get_page(page),)
