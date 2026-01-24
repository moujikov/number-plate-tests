import time
from pipelines import Pipelines

image_paths = [
    'test-images/IMG_0780.jpg',
    'test-images/IMG_0781.jpg',
    'test-images/IMG_0782.jpg',
    'test-images/IMG_0783.jpg',
    'test-images/IMG_0798.jpg',
    'test-images/IMG_0799.jpg',
    ]

start_time = time.perf_counter()
print('___________________________________')

for image_path in image_paths:
    print()
    result = Pipelines.ru_pipeline([image_path])[0]
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
