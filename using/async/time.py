import asyncio


async def async_sum(x, y):
    print("Start: async_sum")
    await asyncio.sleep(0.1)
    print("End: async_sum")
    return x + y

async def long_async_sum(x, y):
    print("Start: long_async_sum")
    # пауза без блокировки event-loop, остальные будут работать в это время
    await asyncio.sleep(1)
    print("End: long_async_sum")
    return x + y

async def composite_runner():
    res1, res2 =  await asyncio.gather(async_sum(1, 2), long_async_sum(10, 20))
    print(res1, res2)

async def main():
    try:
        await composite_runner()
    except asyncio.TimeoutError:
        print("TimeoutError")

if __name__ == '__main__':
    asyncio.run(main())
