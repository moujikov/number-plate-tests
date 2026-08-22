from datetime import datetime
import sys

from common import utils
from .detection import detect, setup

setup()

args = sys.argv[1:]
if args:
  utils.make_gitignored_dir('.runs-artifacts')
  ts = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
  detections = detect(args[0] if len(args) == 1 else args, save_artifacts=f'.runs-artifacts/{ts}-vehicles')

  print("\nDETECTIONS:")
  for detection in detections:
    print(detection)
