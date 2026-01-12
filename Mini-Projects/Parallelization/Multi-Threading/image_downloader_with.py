# with parallel processing:

import requests         # used to hanlde http requests
import time
# this is what allows multithreading :)
from concurrent.futures import ThreadPoolExecutor


def download(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        # storing the data as "write byte" because image file is a raw byte code data.
        with open(file_name, "wb") as image:
            # response.content is used to pull the content (byte code) from the response object.
            image.write(response.content)
            print("\nImage downloaded successfully")
    else:
        print(f"\nImage download failed. Status code: {response.status_code}")


start_time = time.perf_counter()

with ThreadPoolExecutor() as executor:      # just remember the format :)
    for image_num in range(1, 11):      # starts n from 1. ends at 11.

        file_name = "Projects/Parallelization/Image downloader/downloads/image_" + \
            str(image_num)+".jpg"
        url = "https://picsum.photos/200/300"
        # again remember the format: executor.submit(function, arg1, arg2)
        executor.submit(download, url, file_name)


end_time = time.perf_counter()
total_time = end_time - start_time

print("\n-----------------------------------------------------")
# 3 seconds from 12 seconds :)
print(
    f"Total time taken to download all images using Multi-threading: {total_time:.2f} seconds")
