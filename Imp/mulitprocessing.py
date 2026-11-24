import time 
from concurrent.futures import ProcessPoolExecutor #for multiprocessing

#simulation of a task that spends time in computations or calculations instead of external factors - CPU bound tasks
def do_cpu_work(task_id: int, iterations : int = 1000000) -> str:
    res = 0
    for i in range(iterations):
        res += i*i
    return f"Task {task_id} done.. res = {res}"


# run_multiprocessing P1, P2, ...
def run_mp(tasks : int = 5, max_workers: int = 5) -> list[str]:
    res: list[str] =[]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(do_cpu_work, i, 1000000) for i in range(tasks)]

        for fut in futures:
            result = fut.result()
            res.append(result)
    return res


if __name__ == "__main__":
    start = time.perf_counter()
    res = run_mp(tasks=5)
    elpsed = time.perf_counter() - start

    # print("sync results: ")
    print("multi-processing results: ")
    for r in res:
        print(f"{r}")
    print(f"total time taken : {elpsed:.3f}secs")
