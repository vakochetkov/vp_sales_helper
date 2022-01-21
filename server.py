import asyncio
import logging
from aiohttp import web

from constants import SERVER_URL


WEBHOOK_HOST = SERVER_URL
WEBHOOK_URL  = '/wcapi/order'
WEBHOOK_PORT = 8080 # important since wordpress does not allow custom ports

SLEEP_DELAY = 3600


logger = logging.getLogger(__name__)


async def __handler(request):
    logger.info("Handling hook...")
    headers = request.headers
    post_args = await request.post()

    if "WooCommerce" in str(headers.get("User-Agent")):
        data = await request.json()
        logger.info(data)
        callback = request.config_dict["callback"]
        if callback:
            await callback(data)
    return web.Response()

async def on_startup(app):
    logger.warning(f"===== Start listening on {WEBHOOK_HOST}:{WEBHOOK_PORT} =====")

async def on_cleanup(app):
    logger.warning("Clean-up webhook server...")

def init(url, callback):
    app = web.Application()
    app["callback"] = callback
    app.router.add_post(WEBHOOK_URL, __handler)
    logger.warning(f"Register listener for {WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL}")

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

async def run(callback):
    runner = web.AppRunner(init(WEBHOOK_URL, callback))
    await runner.setup()

    try:
        site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)
        await site.start()
        while True:
            await asyncio.sleep(SLEEP_DELAY)
    finally:
        await runner.cleanup()


if __name__ == "__main__": # TEST
    loop = asyncio.get_event_loop() 

    try:
        print("Press Ctrl+C to exit")
        task = loop.create_task(run())
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass
    loop.close()