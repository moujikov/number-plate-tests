from pipelines import Pipelines

number_plate = Pipelines.full_pipeline(['test-images/self-check.jpg'])[0][8][0]
expected_number_plate = 'C364EH178'

if number_plate == expected_number_plate:
  print(f'✅ SELF TEST PASSED: Successfully read number plate: {number_plate}')
else:
  print(f'❌ SELF TEST FAILED: Error reading number plate: expected {expected_number_plate}, but got {number_plate}')
  exit(1)
  
