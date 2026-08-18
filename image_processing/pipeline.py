import warnings
from typing import Callable
from threading import Lock
from matplotlib.pylab import ndarray
import nomeroff_net

from common.types import DetectCountry
from common.logging import logger



ALL_COUNTRIES = (DetectCountry.RU, DetectCountry.BY, 
                 DetectCountry.AM, DetectCountry.GE, 
                 DetectCountry.KZ, DetectCountry.KG, 
                 DetectCountry.UA, DetectCountry.EU)


class LockablePipeline():
  __pipeline: Callable
  __lock: Lock

  def __init__(self, pipeline: Callable):
    self.__pipeline = pipeline
    self.__lock = Lock()

  def __call__(self, inputs, **kwargs):
    with self.__lock:
      return self.__pipeline(inputs, **kwargs)


__cached_pipeline: LockablePipeline | None = None
configured_countries: list[DetectCountry] = []


def setup(*countries: DetectCountry):
  global __cached_pipeline, configured_countries

  if not countries:
    raise ValueError("Countries list cannot be empty")
    
  configured_countries = list(ALL_COUNTRIES if DetectCountry.ALL in countries else countries)

  logger.info(
              f'Preloading recognition models for number plate types:'
              f' {", ".join([c.value for c in configured_countries])}'
             )
  __cached_pipeline = LockablePipeline(__create_pipeline(configured_countries))
  __cached_pipeline([]) # Preload models to avoid first request latency


def call(inputs: list[ndarray], **kwargs):
  if __cached_pipeline is None:
    raise Exception("Pipeline is not initialized")
  
  with warnings.catch_warnings(action="ignore"):  # Ignore detection warnings e.g. 'unknown region'
    detections = __cached_pipeline(inputs, **kwargs)

  for detection in detections:
    if len(detection) > 5:
      regions = detection[5]
      for i in range(len(regions)):
        detected_country = __country_by_class(regions[i])
        if detected_country and detected_country in configured_countries:
          regions[i] = detected_country.value
        else:
          regions[i] = "unknown"

  return detections



def __create_pipeline(countries: list[DetectCountry]) -> Callable:
  classes = __number_plate_classes(countries)

  presets = dict()
  for country in countries:
    presets[__ocr_model(country)] = {
      "for_regions": __country_classes(country),
      "for_count_lines": [1],
      "model_path": "latest"
    }

  return nomeroff_net.pipeline("number_plate_detection_and_reading",
                               presets = presets,
                               classification_options = {
                                 "class_region": classes,
                                 "count_lines": [1]
                               },
                               default_label = classes[0],
                               default_lines_count = 1,
                               upscaling = False,
                               off_number_plate_classification = (len(classes) == 1)
                              )

def __number_plate_classes(countries: list[DetectCountry]) -> list[str]:
  return [region for country in countries for region in __country_classes(country)]

def __country_classes(country: DetectCountry) -> list[str]:  
  if country == DetectCountry.RU:
    return ["ru"]
  elif country == DetectCountry.BY:
    return ["by"]
  elif country == DetectCountry.AM:
    return ["am"]
  elif country == DetectCountry.GE:
    return ["ge"]
  elif country == DetectCountry.KZ:
    return ["kz"]
  elif country == DetectCountry.KG:
    return ["kg"]
  elif country == DetectCountry.UA:
    return ["eu_ua_2004", "eu_ua_2015"]
  elif country == DetectCountry.EU:
    return ["eu"]
  else: 
    raise ValueError(f"Unsupported country: {country.value}")

def __country_by_class(class_name: str) -> DetectCountry | None:  
  if class_name == "ru":
    return DetectCountry.RU
  elif class_name == "by":
    return DetectCountry.BY
  elif class_name == "am":
    return DetectCountry.AM
  elif class_name == "ge":
    return DetectCountry.GE
  elif class_name == "kz":
    return DetectCountry.KZ
  elif class_name == "kg":
    return DetectCountry.KG
  elif class_name == "eu_ua_2004" or class_name == "eu_ua_2015":
    return DetectCountry.UA
  elif class_name == "eu":
    return DetectCountry.EU
  else:
    return None

def __ocr_model(country: DetectCountry) -> str:  
  if country == DetectCountry.RU:
    return "ru"
  elif country == DetectCountry.BY:
    return "by"
  elif country == DetectCountry.AM:
    return "am"
  elif country == DetectCountry.GE:
    return "ge"
  elif country == DetectCountry.KZ:
    return "kz"
  elif country == DetectCountry.KG:
    return "kg"
  elif country == DetectCountry.UA:
    return "eu_ua_2004_2015_efficientnet_b2"
  elif country == DetectCountry.EU:
    return "eu_efficientnet_b2"
  else:
    raise ValueError(f"Unsupported country: {country.value}")
