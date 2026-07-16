import time
import asyncio

# Synchronous: tasks run one after another
def slow_task_sync(name: str, seconds: float):
    time.sleep(seconds)
    print(f"{name} done")

t0 = time.perf_counter()
slow_task_sync("Task A", 2)
slow_task_sync("Task B", 2)
print(f"Sync total: {time.perf_counter() - t0:.2f}s")  # 4s


# Async: tasks run concurrently
async def slow_task_async(name: str, seconds: float):
    await asyncio.sleep(seconds)
    print(f"{name} done")

async def main():
    t0 = time.perf_counter()
    await asyncio.gather(
        slow_task_async("Task A", 2),
        slow_task_async("Task B", 2),
    )
    print(f"Async total: {time.perf_counter() - t0:.2f}s")  # 2s, not 4

asyncio.run(main())