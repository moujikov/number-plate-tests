from enum import Enum
from pathlib import Path

from matplotlib import image
from matplotlib import image
from matplotlib.cm import gray
from matplotlib.pylab import beta
import numpy as np
import cv2 as cv

class Method(Enum):
  INTEGRAL = 0
  LAPLACIAN = 1
  DFT = 2

SAMPLE_WIDTH = 200

def measure(img: np.ndarray, 
            method: Method = Method.INTEGRAL, 
            save_artifacts: str | Path | None = None
           ) -> float:
  """
  Measure the sharpness of a number plate image.

  Args:
    img: np.ndarray, the input image with cropped number plate.
    method: a method to use, INTEGRAL uses all methods and returns mean result
    save_artifacts: path to base filename (.jpg) to save intermediate artifacts to (images, edges, etc.).

  Returns:
    a floating point score from 0.0 (blurriest) to 1.0 (sharpest).

  Raises:
    ValueError: if an unsupported method is specified.
  """

  # Cut outer edge where a numberplate border can affect analisys:
  BORDER_CUTOFF = 0.15
  h, w = img.shape[:2]
  border_width = round(BORDER_CUTOFF * h)
  no_border = img[border_width:-border_width, border_width:-border_width]

  # Unify image sizes (WIDTH=200) to yield consistent sharpness measurements:
  h, w = no_border.shape[:2]
  sample = cv.resize(no_border, (SAMPLE_WIDTH, round(h * SAMPLE_WIDTH / w)), interpolation=cv.INTER_CUBIC)

  if method == Method.LAPLACIAN:
    return __measure_laplacian(sample, save_artifacts)

  if method == Method.DFT:
    return __measure_fft(sample, save_artifacts)

  if method == Method.INTEGRAL:
    return __measure_integral(sample, save_artifacts)



def __measure_laplacian(sample: np.ndarray, 
                        save_artifacts: str | Path | None = None
                       ) -> float:
  grayscale = cv.cvtColor(sample, cv.COLOR_BGR2GRAY)
  edges = cv.Laplacian(grayscale, cv.CV_16S, ksize=5)

  # Filter out noise by applying a Gaussian blur
  smoothed_edges = cv.GaussianBlur(edges, (3, 3), 0)
  # smoothed_edges = edges

  score = smoothed_edges.var()

  HI_SHARPNESS_THRESHOLD = 500000     # Consider everything above this as ideally sharp
  n_score = min(score / HI_SHARPNESS_THRESHOLD, 1.0)

  if save_artifacts:
    edges_grayscale = cv.convertScaleAbs(smoothed_edges, alpha = 1/10)

    contrast_rms = sample.std()

    path = Path(save_artifacts)
    name = path.parent / f'{path.stem}_c-{contrast_rms:.2f}_s-{score:.0f}_ns-{n_score:.2f}'
    cv.imwrite(f'{name}_sample.jpg', sample)
    cv.imwrite(f'{name}_edges.jpg', edges_grayscale)

  return n_score



def __measure_fft(sample: np.ndarray,
                  save_artifacts: str | Path | None = None
                 ) -> float:
  grayscale = cv.cvtColor(sample, cv.COLOR_BGR2GRAY)

  # Split each row into a set of waves using DFT:
  waves = np.array([np.fft.rfft(row) for row in grayscale])

  # Discard zero frequency (first column), phase (imaginary part) and amplitude sign.
  # Leave only pure absolute amplitudes:
  amplitudes = np.abs(np.real(waves[:,1:]))

  # Sample WIDTH=200 yields 100 frequencies, of which low and high should be discarded:
  LO_FRQ_CUTOFF = 8     # Discard low frequencies (gamma variations, shadows, etc.) 
  HI_FRQ_CUTOFF = 40    # Discard high frequencies (noise)
  mid_frq_amplitudes = amplitudes[:, LO_FRQ_CUTOFF:HI_FRQ_CUTOFF]

  score = np.mean(mid_frq_amplitudes)
  MAX_SCORE = 400     # Consider everything above this as ideally sharp
  n_score = min(score / MAX_SCORE, 1.0)

  if save_artifacts:
    map = cv.convertScaleAbs(np.real(amplitudes), alpha = 1/8)
    map = cv.cvtColor(map, cv.COLOR_GRAY2BGR)
    h = map.shape[0]
    cv.line(map, (LO_FRQ_CUTOFF, 0), (LO_FRQ_CUTOFF, h), (0, 0, 255), 1)
    cv.line(map, (HI_FRQ_CUTOFF, 0), (HI_FRQ_CUTOFF, h), (0, 0, 255), 1)

    path = Path(save_artifacts)
    name = path.parent / f'{path.stem}_s-{score:.0f}_ns-{n_score:.2f}'
    cv.imwrite(f'{name}_sample.jpg', sample)
    cv.imwrite(f'{name}_map.jpg', map)

  return n_score



def __measure_integral(sample: np.ndarray,
                       save_artifacts: str | Path | None = None
                      ) -> float:
  measures = []
  measures.append(__measure_laplacian(sample))
  measures.append(__measure_fft(sample))
  n_score = np.mean(measures)

  if save_artifacts:
    path = Path(save_artifacts)
    name = path.parent / f'{path.stem}_ns-{n_score:.2f}'
    cv.imwrite(f'{name}.jpg', sample)

  return n_score
