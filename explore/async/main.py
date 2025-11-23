import asyncio


async def async_sum(x, y):
    await asyncio.sleep(0.1)
    return x + y


async def async_sum_all(*args):
    s = 0
    for x, y in args:
        s += await async_sum(x, y)
    return s


# Раньше, до Python 3.5, для asyncio использовались “yield from” генераторы:
# @asyncio.coroutine
# def old_style():
#     yield from asyncio.sleep(1)

async def download_file(url):
    print(f"Start downloading {url}...")
    await asyncio.sleep(0.1)
    print(f"Finished downloading {url}!")
    return f"{url} downloaded"


async def download_files(tasks):
    return await asyncio.gather(*tasks)


async def future_task(fut):
    await asyncio.sleep(0.5)
    fut.set_result("Future result: 3")


async def usage_future():
    """
    Future — это объект-плейсхолдер: значение, которое будет установлено позже.
    Обычно Future заполняется либо задачей, либо другим кодом.
    """
    # пустой future
    fut = asyncio.Future()
    task = asyncio.create_task(future_task(fut))

    res = await fut
    print(res)

    print(task)  # <Task finished name='Task-14' coro=<future_task() done
    await task


async def long_cancelable_operation():
    try:
        print("long_cancelable_operation started")
        await asyncio.sleep(0.5)
        print("long_cancelable_operation finished")
    except asyncio.CancelledError:
        print("Correct: Time to cancel.")
        raise  # важно пробросить дальше


async def usage_wait_for():
    """
    Как asyncio.wait_for прерывает coroutine:
    1) Coroutine long_task() заворачивают в Task
    2) wait_for параллельно запускает таймер
    3) Если задача не завершилась — wait_for вызывает: task.cancel()
    4) Coroutine отправляется исключение CancelledError
    5) Если coroutine правильно обрабатывает отмену (не проглатывает исключение), задача завершается с ошибкой,
       и wait_for выбрасывает: asyncio.TimeoutError
    """
    try:
        result = await asyncio.wait_for(long_cancelable_operation(), timeout=0.3)
        print(result)
    except asyncio.TimeoutError:
        print("Coroutine was cancelled correctly")


def main():
    c = async_sum(1, 2)
    print(c)  # <coroutine object async_sum at 0x100b58dc0>

    # we need runner
    sum2 = asyncio.run(c)
    print(f'Sum: {sum2}')

    sum_all = asyncio.run(async_sum_all([1, 2], [3, 4]))
    print(f'Sum all: {sum_all}')

    # gather
    tasks = [
        download_file("https://example1.com"),
        download_file("https://example2.org"),
        download_file("https://example3.org")
    ]
    asyncio.run(download_files(tasks))

    # future
    asyncio.run(usage_future())

    # wait_for (timeout)
    asyncio.run(usage_wait_for())


if __name__ == '__main__':
    main()
