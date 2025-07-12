import string
import time
from collections import Counter

start_time = time.perf_counter()

final_counter = Counter()
CHUNK_SIZE = 100000

# chunk_tracker is optional; just validating the chunks are increasing as expected.


def word_counter(each_chunk, chunk_tracker):
    partial_counter = Counter(each_chunk)
    final_counter.update(partial_counter)
    # print(f"\nworking on chunk: {chunk_tracker}")


file_path = "Projects/Parallelization/Multi-Processing/word_counter_large_text.txt"


with open(file_path, "r") as file:
    text = file.read().lower()
    cleaned_text = text.translate(str.maketrans("", "", string.punctuation))
    cleaned_text_tokenized = cleaned_text.split()
    total_chunks = len(cleaned_text_tokenized)
    print(total_chunks)
    chunk_start = 0
    chunk_end = 0
    while True:

        if chunk_end == total_chunks:
            break
        else:
            chunk_start = chunk_end
            if (chunk_end + CHUNK_SIZE) > total_chunks:
                chunk_end = total_chunks
            else:
                chunk_end += CHUNK_SIZE
        each_chunk = cleaned_text_tokenized[chunk_start:chunk_end]
        # chunk_start is optional; only being used for tracking in the function.
        word_counter(each_chunk, chunk_start)

end_time = time.perf_counter()
total_time = end_time - start_time

print("\n-----------------------------------------------------\n")
for word, count in final_counter.most_common(10):
    print(f"{word}: {count}")
print("\n-----------------------------------------------------\n")
print(
    f"Total time taken to count words without Multiprocessing: {total_time:.2f} seconds")
