# without parallel processing:

import requests         # used to hanlde http requests
import time


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


total_time = 0

for image_num in range(1, 11):
    start_time = time.perf_counter()
    file_name = "Projects/Parallelization/Image downloader/downloads/image_" + \
        str(image_num)+".jpg"
    url = "https://picsum.photos/200/300"
    download(url, file_name)
    end_time = time.perf_counter()
    download_time = end_time - start_time
    print(
        f"Total time taken to download image {image_num}: {download_time:.2f} seconds")
    total_time += download_time

print("\n-----------------------------------------------------")
print(
    f"Total time taken to download all images without using Multi-threading: {total_time:.2f} seconds")
