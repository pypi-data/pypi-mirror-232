import numpy as np


def test_sdk(load_test_img, load_sdk_default):
    img = load_test_img
    sdk = load_sdk_default
    result = sdk.process(img)
    assert np.allclose(int(result.mean()), 205)
