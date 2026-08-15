from pytest import mark
from image_processing import sharpness

@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_0', 1.00),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_3', 0.95),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_5', 0.55),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_7', 0.40),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_9', 0.35),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_13', 0.25),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_17', 0.20),

  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_0', 1.00),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_3', 0.85),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_5', 0.50),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_7', 0.35),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_9', 0.30),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_13', 0.20),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_17', 0.15),

  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_0', 1.00),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_3', 0.90),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_5', 0.55),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_7', 0.40),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_9', 0.30),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_13', 0.25),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_17', 0.20)
])
def test_motion_blur(assert_sharpness): assert_sharpness.eval()


@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'video', 'T256HT198', 'frame_1', 1.00),
  (sharpness.Method.LAPLACIAN, 'video', 'T256HT198', 'frame_2', 1.00),
  (sharpness.Method.LAPLACIAN, 'video', 'T256HT198', 'frame_3', 0.85),

  (sharpness.Method.DFT, 'video', 'T256HT198', 'frame_1', 1.00),
  (sharpness.Method.DFT, 'video', 'T256HT198', 'frame_2', 1.00),
  (sharpness.Method.DFT, 'video', 'T256HT198', 'frame_3', 0.80),

  (sharpness.Method.INTEGRAL, 'video', 'T256HT198', 'frame_1', 1.00),
  (sharpness.Method.INTEGRAL, 'video', 'T256HT198', 'frame_2', 1.00),
  (sharpness.Method.INTEGRAL, 'video', 'T256HT198', 'frame_3', 0.85)
])
def test_daytime_perfect_sharpness(assert_sharpness): assert_sharpness.eval()


@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'video', 'P641AO47', 'frame_1', 0.95),
  (sharpness.Method.LAPLACIAN, 'video', 'P641AO47', 'frame_2', 0.60),
  (sharpness.Method.LAPLACIAN, 'video', 'P641AO47', 'frame_3', 0.25),
  (sharpness.Method.LAPLACIAN, 'video', 'P641AO47', 'frame_4', 0.10),
  (sharpness.Method.LAPLACIAN, 'video', 'P641AO47', 'frame_5', 0.10),

  (sharpness.Method.DFT, 'video', 'P641AO47', 'frame_1', 0.90),
  (sharpness.Method.DFT, 'video', 'P641AO47', 'frame_2', 0.70),
  (sharpness.Method.DFT, 'video', 'P641AO47', 'frame_3', 0.45),
  (sharpness.Method.DFT, 'video', 'P641AO47', 'frame_4', 0.35),
  (sharpness.Method.DFT, 'video', 'P641AO47', 'frame_5', 0.30),

  (sharpness.Method.INTEGRAL, 'video', 'P641AO47', 'frame_1', 0.95),
  (sharpness.Method.INTEGRAL, 'video', 'P641AO47', 'frame_2', 0.65),
  (sharpness.Method.INTEGRAL, 'video', 'P641AO47', 'frame_3', 0.35),
  (sharpness.Method.INTEGRAL, 'video', 'P641AO47', 'frame_4', 0.25),
  (sharpness.Method.INTEGRAL, 'video', 'P641AO47', 'frame_5', 0.20)
])
def test_twighlight_mediocre_sharpness(assert_sharpness): assert_sharpness.eval()


@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_1', 0.75),
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_2', 0.65),
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_3', 0.20),
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_4', 0.10),
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_5', 0.05),
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_6', 0.00),
  (sharpness.Method.LAPLACIAN, 'video', 'A780KC198', 'frame_7', 0.00),

  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_1', 0.95),
  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_2', 0.80),
  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_3', 0.50),
  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_4', 0.30),
  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_5', 0.25),
  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_6', 0.15),
  (sharpness.Method.DFT, 'video', 'A780KC198', 'frame_7', 0.05),

  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_1', 0.85),
  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_2', 0.75),
  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_3', 0.35),
  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_4', 0.20),
  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_5', 0.15),
  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_6', 0.10),
  (sharpness.Method.INTEGRAL, 'video', 'A780KC198', 'frame_7', 0.05),
])
def test_nighttime_low_sharpness(assert_sharpness): assert_sharpness.eval()


@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'photo', 'M608AA198', 'low_contrast', 0.35),
  (sharpness.Method.LAPLACIAN, 'photo', 'C364EH178', 'low_contrast_low_res', 0.25),

  (sharpness.Method.DFT, 'photo', 'M608AA198', 'low_contrast', 0.60),
  (sharpness.Method.DFT, 'photo', 'C364EH178', 'low_contrast_low_res', 0.50),

  (sharpness.Method.INTEGRAL, 'photo', 'M608AA198', 'low_contrast', 0.50),
  (sharpness.Method.INTEGRAL, 'photo', 'C364EH178', 'low_contrast_low_res', 0.40),
])
def test_low_contrast(assert_sharpness): assert_sharpness.eval()


@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'photo', 'O656OO178', 'hi_contrast', 1.00),
  (sharpness.Method.LAPLACIAN, 'photo', 'P035HT198', 'hi_contrast_low_res', 0.70),

  (sharpness.Method.DFT, 'photo', 'O656OO178', 'hi_contrast', 1.00),
  (sharpness.Method.DFT, 'photo', 'P035HT198', 'hi_contrast_low_res', 1.00),

  (sharpness.Method.INTEGRAL, 'photo', 'O656OO178', 'hi_contrast', 1.00),
  (sharpness.Method.INTEGRAL, 'photo', 'P035HT198', 'hi_contrast_low_res', 0.85),
])
def test_high_contrast(assert_sharpness): assert_sharpness.eval()


@mark.parametrize(['method', 'category', 'number_plate', 'variant', 'expected'], [
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_9', 0.35),
  (sharpness.Method.LAPLACIAN, 'artificial', 'T256HT198', 'motion_blur_9_noisy', 0.40),

  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_9', 0.30),
  (sharpness.Method.DFT, 'artificial', 'T256HT198', 'motion_blur_9_noisy', 0.35),

  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_9', 0.30),
  (sharpness.Method.INTEGRAL, 'artificial', 'T256HT198', 'motion_blur_9_noisy', 0.40),
])
def test_noise(assert_sharpness): assert_sharpness.eval()
