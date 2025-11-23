import asyncio


async def async_sum(x, y):
    await asyncio.sleep(1)
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

def main():
    c = async_sum(1, 2)
    print(c) # <coroutine object async_sum at 0x100b58dc0>

    # we need runner
    sum2 = asyncio.run(c)
    print(f'Sum: {sum2}')

    sum_all = asyncio.run(async_sum_all([1, 2], [3, 4]))
    print(f'Sum all: {sum_all}')

if __name__ == '__main__':
    main()
