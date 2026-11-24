import time 
from concurrent.futures import ThreadPoolExecutor #this is modern and clean way to manage threads


#simulation of a task that spends time waiting instead of computing - IO bound task
def do_work(task_id: int, duration: float=0.1) -> str:
    time.sleep(duration)
    return f"{task_id} done.. "

#synchronous tasks
# def run_sync(tasks: int = 10) -> list[str]:
    # res: list[str] = []
    # for i in range(tasks):
    #     op = do_work(i, duration=0.1) #100ms wait
    #     res.append(op)
    # return res 
def run_threading(tasks: int=5, max_workers: int = 5) -> list[str]: #this is modern way.. 
    res: list[str] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(do_work, i, 0.1) for i in range(tasks)]

        # grab the results:
        for future in futures:
            result = future.result()
            res.append(result)
    return res

if __name__ == "__main__":
    start = time.perf_counter()
    res = run_threading(tasks=5)
    elpsed = time.perf_counter() - start

    # print("sync results: ")
    print("concurrent threads results: ")
    for r in res:
        print(f"{r}")
    print(f"total time taken : {elpsed:.3f}secs")
