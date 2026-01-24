from pipelines import full_pipeline
from test_images import self_check_test_image_paths

number_plate = full_pipeline(self_check_test_image_paths)[0][8][0]
expected_number_plate = 'C364EH178'

if number_plate == expected_number_plate:
  print(f'✅ SELF TEST PASSED: Successfully read number plate: {number_plate}')
else:
  print(f'❌ SELF TEST FAILED: Error reading number plate: expected {expected_number_plate}, but got {number_plate}')
  exit(1)
  
