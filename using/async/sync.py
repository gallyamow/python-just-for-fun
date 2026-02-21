import asyncio

lock = asyncio.Lock()


# TODO:
async def worker(name):
    print(f"{name} waiting for lock")
    async with lock:
        print(f"{name} acquired lock")
        await asyncio.sleep(1)
    print(f"{name} released lock")


async def main():
    await asyncio.gather(worker("A"), worker("B"))


if __name__ == "__main__":
    asyncio.run(main())
