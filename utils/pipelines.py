from nomeroff_net import pipeline

__full_pipeline = None
__ru_by_pipeline = None
__ru_pipeline = None

def full_pipeline(inputs, **kwargs):
  pipeline = __get_full_pipeline()
  return pipeline(inputs, **kwargs)
  

def ru_by_pipeline(inputs, **kwargs):
  pipeline = __get_ru_by_pipeline()
  return pipeline(inputs, **kwargs)


def ru_pipeline(inputs, **kwargs):
  pipeline = __get_ru_pipeline()
  return pipeline(inputs, **kwargs)


def __get_full_pipeline():
  global __full_pipeline
  if __full_pipeline is None:
    __full_pipeline = pipeline("number_plate_detection_and_reading",
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
        }
      },
      classification_options = {
        "class_region": ["ru", "by", "am", "ge", "kz", "kg"],
        "count_lines": [1]
      },
      # image_loader="turbo",
      default_label="ru",
      default_lines_count=1,
      upscaling=False,
      off_number_plate_classification=False
      )
  return __full_pipeline

def __get_ru_by_pipeline():
  global __ru_by_pipeline
  if __ru_by_pipeline is None:
    __ru_by_pipeline = pipeline("number_plate_detection_and_reading",
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
      # image_loader="turbo",
      default_label="ru",
      default_lines_count=1,
      upscaling=False,
      off_number_plate_classification=False
      )
  return __ru_by_pipeline

def __get_ru_pipeline():
  global __ru_pipeline
  if __ru_pipeline is None:
    __ru_pipeline = pipeline("number_plate_detection_and_reading",
      presets={
        "ru": {
            "for_regions": ["ru"],
            "for_count_lines": [1],
            "model_path": "latest"
        }
      },
      # image_loader="turbo",
      default_label="ru",
      default_lines_count=1,
      upscaling=False,
      off_number_plate_classification=True
      )
  return __ru_pipeline
