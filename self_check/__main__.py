from test_images import self_check_test_image_paths
from utils.pipelines import full_pipeline
from utils.jpeg import read_local_images

number_plate = full_pipeline(read_local_images(self_check_test_image_paths))[0][8][0]
expected_number_plate = 'C364EH178'

if number_plate == expected_number_plate:
  print(f'✅ SELF TEST PASSED: Successfully read number plate: {number_plate}')
else:
  print(f'❌ SELF TEST FAILED: Error reading number plate: expected {expected_number_plate}, but got {number_plate}')
  exit(1)
  
