import asyncio

async def say_hello_async():
    print("Hello, Async World!")

async def do_something_else():
    print("Starting another task...")

async def main():
    # Schedule both tasks to run concurrently
    await asyncio.gather(
        say_hello_async(),
        do_something_else(),
    )

asyncio.run(main())