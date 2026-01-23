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


number_plate = number_plate_detection_and_reading(['self-check/self-check.jpg'])[0][8][0]
expected_number_plate = 'C364EH178'
if number_plate == expected_number_plate:
  print(f'✅ SELF TEST PASSED: Successfully read number plate: {number_plate}')
else:
  print(f'❌ SELF TEST FAILED: Error reading number plate: expected {expected_number_plate}, but got {number_plate}')
  exit(1)
  
