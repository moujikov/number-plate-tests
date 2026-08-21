import os

def make_temp_dir(dir: str):
  os.makedirs(dir, exist_ok=True)
  with open(f"{dir}/.gitignore", "w") as f:
    f.write("# This file was automatically created, do not edit manually\n"
            "*\n")
