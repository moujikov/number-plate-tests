import time
from common.types import DetectCountry
from image_processing import jpeg, detections

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
    "region": "UA",
    "country": "UA"
  }
]

print(f'Downloading models:')
detections.setup(DetectCountry.ALL)  # Preload all models

start_time = time.perf_counter()
print(f'Running self-check tests:')

for test in tests:
  country = test["country"]
  expected_region = test["region"]
  expected_number_plate = test["number_plate"]

  results = detections.detect(jpeg.read_local_image(f'self_check/images/{test["file"]}'))

  found = False
  for result in results:
    region = result["region"]
    number_plate = result["text"]

    if region == expected_region and number_plate == expected_number_plate:
      print(f'✔️ {country}: successfully read number plate {expected_number_plate}')
      found = True
      break

  if not found:
    print(f'❌ {country}: error reading number plate {expected_number_plate} – '
          f'got {", ".join([f'{r["text"]} [{r["region"]}]' for r in results])} instead')
    failed = True

print(f'---------------------------------')
elapsed_time = time.perf_counter() - start_time

if failed:
  print(f'🛑 SELF TEST FAILED in {elapsed_time:.2f} sec.')
  exit(1)

print(f'✅ SELF TEST PASSED in {elapsed_time:.2f} sec.')
