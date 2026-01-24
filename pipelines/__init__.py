from nomeroff_net import pipeline

class Pipelines:
  __full_pipeline = None
  __ru_pipeline = None


  @classmethod
  def full_pipeline(cls, inputs, **kwargs):
    pipeline = cls.__get_full_pipeline()
    return pipeline(inputs, **kwargs)
    
  @classmethod
  def ru_by_pipeline(cls, inputs, **kwargs):
    pipeline = cls.__get_ru_by_pipeline()
    return pipeline(inputs, **kwargs)
  
  @classmethod
  def ru_pipeline(cls, inputs, **kwargs):
    pipeline = cls.__get_ru_pipeline()
    return pipeline(inputs, **kwargs)


  @classmethod
  def __get_full_pipeline(cls):
    if cls.__full_pipeline is None:
      cls.__full_pipeline = pipeline("number_plate_detection_and_reading",
        presets={
          "ru": {
              "for_regions": ["ru", "eu_ua_ordlo_lpr", "eu_ua_ordlo_dpr"],
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
        image_loader="turbo",
        default_label="ru",
        default_lines_count=1,
        upscaling=False,
        off_number_plate_classification=False
        )
    return cls.__full_pipeline
  
  @classmethod
  def __get_ru_by_pipeline(cls):
    if cls.__full_pipeline is None:
      cls.__full_pipeline = pipeline("number_plate_detection_and_reading",
        presets={
          "ru": {
              "for_regions": ["ru", "eu_ua_ordlo_lpr", "eu_ua_ordlo_dpr"],
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
        image_loader="turbo",
        default_label="ru",
        default_lines_count=1,
        upscaling=False,
        off_number_plate_classification=False
        )
    return cls.__full_pipeline

  @classmethod
  def __get_ru_pipeline(cls):
    if cls.__ru_pipeline is None:
      cls.__ru_pipeline = pipeline("number_plate_detection_and_reading",
        presets={
          "ru": {
              "for_regions": ["ru", "eu_ua_ordlo_lpr", "eu_ua_ordlo_dpr"],
              "for_count_lines": [1],
              "model_path": "latest"
          }
        },
        image_loader="turbo",
        default_label="ru",
        default_lines_count=1,
        upscaling=False,
        off_number_plate_classification=True
        )
    return cls.__ru_pipeline
