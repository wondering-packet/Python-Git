import string
import time
from collections import Counter

start_time = time.perf_counter()

with open("Projects/Parallelization/Multi-Processing/word_counter_large_text.txt", "r") as file:
    text = file.read().lower()
    cleaned_text = text.translate(str.maketrans("", "", string.punctuation))

word_counts = Counter(cleaned_text.split())
for word, count in word_counts.most_common(10):
    print(f"{word}: {count}")

end_time = time.perf_counter()
total_time = end_time - start_time

print("\n-----------------------------------------------------")
print(
    f"Total time taken to count words without Multiprocessing: {total_time:.2f} seconds")
