import string
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter

start_time = time.perf_counter()

final_counter = Counter()

CHUNK_SIZE = 100000

# chunk_number is optional; just validating the chunks are increasing as expected.


def word_counter(file_chunk):
    final_counter = Counter()
    text = file_chunk.lower()
    cleaned_text = text.translate(
        str.maketrans("", "", string.punctuation))
    cleaned_text_tokenized = cleaned_text.split()
    return Counter(cleaned_text_tokenized)


file_path = "Projects/Parallelization/Multi-Processing/word_counter_large_text.txt"

with ProcessPoolExecutor(max_workers=4) as executor:
    futures = []
    with open(file_path, "r") as file:
        while True:
            file_load_start_time = time.perf_counter()
            file_chunk = file.read(5 * 1024 * 1024)  # 5 MB per chunk
            print(
                f"Read took: {time.perf_counter() - file_load_start_time:.2f}s")
            if not file_chunk:
                break
            processing_start_time = time.perf_counter()
            futures.append(executor.submit(word_counter, file_chunk))
            print(
                f"Submit took: {time.perf_counter() - processing_start_time:.2f}s")
        for each_future in as_completed(futures):
            final_counter.update(each_future.result())
end_time = time.perf_counter()
total_time = end_time - start_time

print("\n-----------------------------------------------------\n")
for word, count in final_counter.most_common(10):
    print(f"{word}: {count}")
print("\n-----------------------------------------------------\n")
print(
    f"Total time taken to count words with Multiprocessing: {total_time:.2f} seconds")
