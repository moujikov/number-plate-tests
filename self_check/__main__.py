import time
from image_processing.pipelines import full_pipeline
from image_processing.jpeg import read_local_images

failed = False

tests = [
  {
    "file" : "ru.jpg", 
    "number_plate": "C364EH178",
    "region": "RU",
    "country": "RU"
  },
  {
    "file" : "by.jpg", 
    "number_plate": "9559OE7",
    "region": "BY",
    "country": "BY"
  },
  {
    "file" : "am.jpg", 
    "number_plate": "01OA090",
    "region": "AM",
    "country": "AM"
  },
  {
    "file" : "ge.jpg", 
    "number_plate": "MA001QE",
    "region": "GE",
    "country": "GE"
  },
  {
    "file" : "kz.jpg", 
    "number_plate": "410ARZ11",
    "region": "KZ",
    "country": "KZ"
  },
  {
    "file" : "kg.jpg", 
    "number_plate": "04892AAH",
    "region": "KG",
    "country": "KG"
  },
  {
    "file" : "ee.jpg", 
    "number_plate": "396KGR",
    "region": "EU",
    "country": "EE"
  },
  {
    "file" : "lt.jpg", 
    "number_plate": "EGL076",
    "region": "EU",
    "country": "LT"
  },
  {
    "file" : "de.jpg", 
    "number_plate": "TFS1941H",
    "region": "EU",
    "country": "DE"
  },
  {
    "file" : "ua.jpg", 
    "number_plate": "BX5100HA",
    "region": "EU_UA_2015",
    "country": "UA"
  }
]

print(f'Downloading models:')
full_pipeline([])  # Preload models

start_time = time.perf_counter()
print(f'Running self-check tests:')

for test in tests:
  detections = full_pipeline(read_local_images(f'self_check/test_images/{test["file"]}'))
  region = detections[0][5][0].upper()
  number_plate = detections[0][8][0]

  country = test["country"]
  expected_region = test["region"]
  expected_number_plate = test["number_plate"]

  if region == expected_region and number_plate == expected_number_plate:
    print(f'✔️ {country}: successfully read number plate {expected_number_plate}')
  else:
    print(f'❌ {country}: error reading number plate {expected_number_plate} [{expected_region}], got {number_plate} [{region}] instead')
    failed = True

print(f'---------------------------------')
elapsed_time = time.perf_counter() - start_time

if failed:
  print(f'🛑 SELF TEST FAILED in {elapsed_time:.2f} sec.')
  exit(1)

print(f'✅ SELF TEST PASSED in {elapsed_time:.2f} sec.')
