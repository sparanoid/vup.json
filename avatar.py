import httpx
import os
import json

data_file = 'dist/vup-full-array.json'
sort_key = 'followers'
output_dir = 'tmp'
items_limit = 300

# Counters for the summary
counter_total = 0
counter_downloaded = 0
counter_skipped = 0

# Download and save the avatar
def download_image(url: str, folder: str, filename: str, obj):
    global counter_total, counter_downloaded, counter_skipped
    file_path = os.path.join(folder, filename)
    if not os.path.exists(file_path):
        response = httpx.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"{items_limit}/{counter_total + 1} Downloaded {filename} in {folder} ({sort_key}: {obj[sort_key]})")
            counter_total += 1
            counter_downloaded += 1
        else:
            print(f"Failed to download {url}")
    else:
        print(f"{items_limit}/{counter_total + 1} File {filename} already exists in {folder} ({sort_key}: {obj[sort_key]})")
        counter_total += 1
        counter_skipped += 1

# Read and sort JSON
with open(data_file, 'r') as file:
    json_arr = json.load(file)

sorted_json_arr = sorted(json_arr, key=lambda item: item[sort_key], reverse=True)

# Main process
for item in sorted_json_arr[:items_limit]:
    folder_name = f"{output_dir}/{item['name']}"
    img_src = f"https://i0.hdslb.com{item['face']}"

    # Create directory if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Extract filename from URL
    filename = img_src.split('/')[-1]
    download_image(img_src, folder_name, filename, item)

# Print summary
print(f"\nSummary:\nImages Downloaded: {counter_downloaded}\nImages Skipped: {counter_skipped}")
