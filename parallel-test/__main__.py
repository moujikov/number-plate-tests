from nomeroff_net import pipeline
import time


number_plate_detection_and_reading = pipeline("number_plate_detection_and_reading_runtime",
                                              presets={
                                                "ru": {
                                                    "for_regions": 
                                                      ["ru", "eu_ua_ordlo_lpr", "eu_ua_ordlo_dpr"],
                                                    "for_count_lines": [1],
                                                    "model_path": "latest"
                                                },
                                                "by": {
                                                    "for_regions": ["by"],
                                                    "for_count_lines": [1],
                                                    "model_path": "latest"
                                                },
                                              },
                                              classification_options = {
                                                "class_region": ["ru", "by"],
                                                "count_lines": [1]
                                              },
                                              image_loader="turbo",
                                              default_label="ru",
                                              default_lines_count=1,
                                              upscaling=False,
                                              off_number_plate_classification=False
                                              )



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

results = number_plate_detection_and_reading(image_paths, num_workers=3, batch_size=3)
for result in results:
    print()
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
