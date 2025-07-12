import time
import sys
sys.set_int_max_str_digits(5000000)


def calculate_fact(n):
    result = 1
    for i in range(1, n+1):
        result *= i
    return str(result)[:10]


numbers = [50000, 60000, 70000, 80000, 90000, 100000]

total_time = 0

for each_number in numbers:
    start_time = time.perf_counter()
    print(calculate_fact(each_number))
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Time taken to calculate {each_number}!: {execution_time:.2f}")
    total_time += execution_time

print("\n-----------------------------------------------------")
print(
    f"Total time taken to calculate without using Multi-processing: {total_time:.2f} seconds")
