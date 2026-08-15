import os

if not os.path.exists('.tests-artifacts'):
  os.makedirs(f'.tests-artifacts')
  
  with open('.tests-artifacts/.gitignore', 'w') as f:
    f.write('*\n')
