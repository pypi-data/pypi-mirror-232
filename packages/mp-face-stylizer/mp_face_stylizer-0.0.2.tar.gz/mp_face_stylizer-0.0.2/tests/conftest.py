import cv2
import pytest

from mp_face_stylizer.sdk import FaceStylizer


@pytest.fixture
def load_test_img(request):
    img = cv2.imread("imgs/business-person.png")
    return img


@pytest.fixture
def load_sdk_default(request):
    sdk = FaceStylizer(model_asset_path="models/face_stylizer.task")
    return sdk


@pytest.fixture
def load_sdk_color_ink(request):
    sdk = FaceStylizer(model_asset_path="models/face_stylizer_color_ink.task")
    return sdk


@pytest.fixture
def load_sdk_oil_painting(request):
    sdk = FaceStylizer(model_asset_path="models/face_stylizer_oil_painting.task")
    return sdk
