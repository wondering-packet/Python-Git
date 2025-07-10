import string
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter

start_time = time.perf_counter()

final_counter = Counter()       # will be used as the parent counter.

CHUNK_SIZE = 100000     # chunk size means the number of words in this script.

# we are doing lower(), translate(), split() in this worker function.
# finally the counter is sent back as output.


def word_counter(file_chunk):
    text = file_chunk.lower()
    cleaned_text = text.translate(
        str.maketrans("", "", string.punctuation))
    cleaned_text_tokenized = cleaned_text.split()
    # this counter will be appended to the parent counter later.
    return Counter(cleaned_text_tokenized)


file_path = "Projects/Parallelization/Multi-Processing/word_counter_large_text.txt"

# max 4 cpu cores will be utilized.
with ProcessPoolExecutor(max_workers=4) as executor:
    futures = []        # our future (task) holder.
    with open(file_path, "r") as file:
        while True:
            file_load_start_time = time.perf_counter()
            # 5 MB per chunk. safeguard against accidentally reading up extremely large amount of data.
            # also, with this we are now doing future (individual task) in 5 MB chunks.
            file_chunk = file.read(5 * 1024 * 1024)
            print(
                f"Read took: {time.perf_counter() - file_load_start_time:.2f}s")
            if not file_chunk:
                break
            processing_start_time = time.perf_counter()
            # spinning up processes using executor.submit(function_name, argument_for_function).
            # we are also appending this future (tast) into futures (tasks) list.
            futures.append(executor.submit(word_counter, file_chunk))
            print(
                f"Submit took: {time.perf_counter() - processing_start_time:.2f}s")
        # as_completed allows us to process output based on execution time.
        # here, we are looping over futures based on execution time,
        # then finally appending all future's result (which is the child counter in word_counter()) to the parent counter.
        for each_future in as_completed(futures):
            final_counter.update(each_future.result())
end_time = time.perf_counter()
total_time = end_time - start_time

print("\n-----------------------------------------------------\n")
# printing top 10 words.
for word, count in final_counter.most_common(10):
    print(f"{word}: {count}")
print("\n-----------------------------------------------------\n")
print(
    f"Total time taken to count words with Multiprocessing: {total_time:.2f} seconds")

# NOTE: even though we are doing multiprocessing, the processing time is actually more than without it.
# reason is: by adding processes, we are adding some overhead which in our case is quite a bit.
# even though our processes themselves are executing in parallel thus reducing execution time individually,
# this still doesn't compensate for the time added by overhead operations.
# the goal should always be so that the execution time overly compensates for the overhead time
# which in turn makes our program faster overall, however this is not the case here.
# why? we are not actually doing CPU-heavy tasks here. thus the time saved on CPU processing is marginal
# & thus not able to compensate for the overhead time.
# multiporcessing would be useful if we were doing CPU-heavy tasks.
