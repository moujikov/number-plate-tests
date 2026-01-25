import time
from test_images import all_test_image_paths
from utils.pipelines import ru_by_pipeline
from utils.jpeg import read_local_images


start_time = time.perf_counter()
print('___________________________________')

for image in read_local_images(all_test_image_paths):
    print()
    result = ru_by_pipeline([image])[0]
    # image = result[0]
    detections = list(zip(*result[1:]))  # skip image
    for detection in detections:
        bbox = detection[0]
        point = detection[1]
        zone = detection[2]
        region_id = detection[3]
        region_name = detection[4]
        count_line = detection[5]
        confidence = detection[6]
        text = detection[7]
        print(f'{text} | {region_name} | {confidence}')

elapsed_time = time.perf_counter() - start_time
print(f'\nDone in {elapsed_time:.2f} sec.')
