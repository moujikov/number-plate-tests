import time

from image_processing.number_plates import pipeline
from ..assets import all_test_image_paths
from common.types import DetectCountry
from image_processing import jpeg

start_time = time.perf_counter()
print('\nPreloading models...')
pipeline.setup(DetectCountry.RU, DetectCountry.BY)

elapsed_time = time.perf_counter() - start_time
print(f'\nDone in {elapsed_time:.2f} sec.')


start_time = time.perf_counter()
print('\nProcessing images...')

for image in jpeg.read_local_images(all_test_image_paths):
    print()
    result = pipeline.call([image])[0]
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
