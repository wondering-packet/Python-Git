# adding as_completed as well this time.
# as_completed takes a list of futures (i.e. tasks) & returns the ouput based on execution time.
# so if task n completed before task n+5, then n's output is returned first.
# this helps in providing an update as tasks are completed.
# e.g. you are viewing a webpage, here you will want the UI elements to start appearing based
# on fetch time as soon as possible (instead of waiting for the entire page to load before it displays).
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import sys
sys.set_int_max_str_digits(5000000)


def calculate_fact(n):
    result = 1
    for i in range(1, n+1):
        result *= i
    return str(result)[:10]


numbers = [50000, 60000, 70000, 80000, 90000, 100000]

start_time = time.perf_counter()

with ProcessPoolExecutor() as executor:
    # futures (tasks) is your list which is holding all the future (task). Note that all future are executed inside the [] block
    futures = [executor.submit(calculate_fact, each_number)
               for each_number in numbers]
    # as_completed is being used on "futures" to return tasks in the order of their completion time.
    for future in as_completed(futures):
        print(future.result())


end_time = time.perf_counter()
total_time = end_time - start_time

print("\n-----------------------------------------------------")
print(
    f"Total time taken to calculate with Multiprocessing: {total_time:.2f} seconds")
