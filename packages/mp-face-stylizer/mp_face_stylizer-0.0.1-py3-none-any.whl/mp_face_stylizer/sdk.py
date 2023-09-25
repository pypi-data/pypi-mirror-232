import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceStylizer:
    def __init__(self, model_asset_path):
        self.base_options = python.BaseOptions(model_asset_path=model_asset_path)
        self.options = vision.FaceStylizerOptions(base_options=self.base_options)
        self.stylizer = vision.FaceStylizer.create_from_options(self.options)

    def process(self, bgr_image):
        """Run stylizer on BGR image input"""
        image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        stylized_image = self.stylizer.stylize(image)

        if stylized_image is not None:
            return stylized_image.numpy_view()
        return None
