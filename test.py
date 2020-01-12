import asyncio
async def func(i):
    print("111111111")
tasks = [asyncio.ensure_future(func(i)) for i in range(0, 11)]
print(tasks)