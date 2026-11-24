#its' almost similar to threads;
import time
import asyncio

async def do_work(task_id: int, durations: float = 0.1)-> str:
    await asyncio.sleep(durations)
    return f"task {task_id} done.. "

# let's see how long does the computation task takes :
#
# output: it took 3 times more time than multiprocessing :
# [total time taken : 0.355secs] 
async def do_cpu_work(task_id: int, iterations : int = 1000000) -> str:
    res = 0
    for i in range(iterations):
        res += i*i
    return f"Task {task_id} done.. res = {res}"


async def run_asyncio(tasks: int= 5) -> list[str]:
    # task_list = [do_work(i, i) for i in range(tasks)]
    # task_list = [do_cpu_work(i) for i in range(tasks)] 

    # res = await asyncio.gather(*task_list) #asterisk is important here.. 
    # return res

    # ------ learn the flow or manual way:

    # events = {}
    # for i in range(tasks):
    #     start = time.perf_counter()
    #     events[i] = asyncio.create_task(do_work(i, i*0.1))

    # for i in events:
    #     start = time.perf_counter()
    #     res = await events[i]
    #     print(f"task {i} done.. in time: {time.perf_counter()-start:.6f}")


    # -------the entire things is manual but in async we get gather or bulk task/co-routines creation option like:
    
    events = [do_work(i, i) for i in range(tasks)] #look this is coroutines
    res = await asyncio.gather(*events) #asterisk -> unpacking the list
    return res


    print("All tasks done..")

if __name__ == "__main__":
    start = time.perf_counter()
    res = asyncio.run(run_asyncio(tasks=5))
    elapsed = time.perf_counter() - start

    print("asyncio tasks results: ")
    print(res)
    for r in res:
        print(f"{r}")
    print(f"total time taken : {elapsed:.3f}secs")
