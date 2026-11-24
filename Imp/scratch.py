import asyncio 
import time 




async def do_work(task_id: int, durations: float = 0.1)-> str:
    await asyncio.sleep(durations)
    return f"task {task_id} done.. "



async def main():
    #co-routine
    # coroutine_object = do_work(1, 0.1) #these are functions whose executions we can pause
    # print(coroutine_object)

    # coroutine_res = await coroutine_object
    # print(coroutine_res)

    # tasks:
    #  <Task pending name='Task-2' coro=<do_work() running at /home/kradarsh/Desktop/ML_core/Imp/scratch.py:7>>
                    # here it's the co-routine created then ran  
    
    task = asyncio.create_task(do_work(1,0.1))
    print(task)


    task_res = await task 
    print(task_res)



if __name__ == "__main__":
    start = time.perf_counter()
    asyncio.run(main()) #event loop
    print(f"Time took: {time.perf_counter()-start}")