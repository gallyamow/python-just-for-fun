import asyncio

# TODO:
async def producer(q):
    for i in range(5):
        await asyncio.sleep(0.2)
        await q.put(i)
        print(f"Produced {i}")

async def consumer(q):
    while True:
        item = await q.get()
        print(f"Consumed {item}")
        q.task_done()

async def main():
    q = asyncio.Queue()
    await asyncio.gather(producer(q), consumer(q))

if __name__ == '__main__':
    asyncio.run(main())
