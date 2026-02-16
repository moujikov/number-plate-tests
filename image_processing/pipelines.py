from collections.abc import Callable
from threading import Lock
from nomeroff_net import pipeline as __pipeline


class LockablePipeline(Callable):
  __pipeline: Callable
  __lock: Lock

  def __init__(self, pipeline: Callable):
    self.__pipeline = pipeline
    self.__lock = Lock()

  def __call__(self, inputs, **kwargs):
    with self.__lock:
      return self.__pipeline(inputs, **kwargs)


__cached_pipeline: LockablePipeline | None = None


def setup_full_pipeline():
  global __cached_pipeline
  __cached_pipeline = LockablePipeline(__create_full_pipeline())
  __cached_pipeline([]) # Preload models to avoid first request latency

def setup_ru_by_pipeline():
  global __cached_pipeline
  __cached_pipeline = LockablePipeline(__create_ru_by_pipeline())
  __cached_pipeline([]) # Preload models to avoid first request latency

def setup_ru_pipeline():
  global __cached_pipeline
  __cached_pipeline = LockablePipeline(__create_ru_pipeline())
  __cached_pipeline([]) # Preload models to avoid first request latency


def pipeline(inputs, **kwargs):
  if __cached_pipeline is None:
    raise Exception("Pipeline is not initialized")
  return __cached_pipeline(inputs, **kwargs)


def __create_full_pipeline():
  return __pipeline("number_plate_detection_and_reading",
    presets={
      "ru": {
          "for_regions": ["ru"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "by": {
          "for_regions": ["by"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "am": {
          "for_regions": ["am"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "ge": {
          "for_regions": ["ge"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "kz": {
          "for_regions": ["kz"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "kg": {
          "for_regions": ["kg"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "eu_ua_2004_2015_efficientnet_b2": {
          "for_regions": ["eu_ua_2004", "eu_ua_2015"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "eu_efficientnet_b2": {
          "for_regions": ["eu", "xx_unknown"],
          "for_count_lines": [1],
          "model_path": "latest"
      }
    },
    classification_options = {
      "class_region": ["ru", "by", "am", "ge", "kz", "kg", "eu_ua_2004", "eu_ua_2015", "eu_ua_1995"],
      "count_lines": [1]
    },
    default_label="ru",
    default_lines_count=1,
    upscaling=False,
    off_number_plate_classification=False
    )

def __create_ru_by_pipeline():
  return __pipeline("number_plate_detection_and_reading",
    presets={
      "ru": {
          "for_regions": ["ru"],
          "for_count_lines": [1],
          "model_path": "latest"
      },
      "by": {
          "for_regions": ["by"],
          "for_count_lines": [1],
          "model_path": "latest"
      }
    },
    classification_options = {
      "class_region": ["ru", "by"],
      "count_lines": [1]
    },
    default_label="ru",
    default_lines_count=1,
    upscaling=False,
    off_number_plate_classification=False
    )

def __create_ru_pipeline():
  return __pipeline("number_plate_detection_and_reading",
    presets={
      "ru": {
          "for_regions": ["ru"],
          "for_count_lines": [1],
          "model_path": "latest"
      }
    },
    default_label="ru",
    default_lines_count=1,
    upscaling=False,
    off_number_plate_classification=True
    )
