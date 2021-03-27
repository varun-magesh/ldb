import asyncio
from dbus_next.aio import MessageBus
from dbus_next import Variant

loop = asyncio.get_event_loop()
async def test(pid):
    bus = await MessageBus().connect()

    introspection = await bus.introspect(f'org.pwmt.zathura.PID-{pid}', '/org/pwmt/zathura')
    proxy_object = bus.get_proxy_object(f'org.pwmt.zathura.PID-{pid}', \
                                        '/org/pwmt/zathura', \
                                        introspection) \

    interface = proxy_object.get_interface('org.pwmt.zathura')

    # Use get_[PROPERTY] and set_[PROPERTY] with the property in
    # snake case to get and set the property.

    bar_value = await interface.get_pagenumber()
    return bar_value

def get_page(pid):
    return loop.run_until_complete(test(pid),)
