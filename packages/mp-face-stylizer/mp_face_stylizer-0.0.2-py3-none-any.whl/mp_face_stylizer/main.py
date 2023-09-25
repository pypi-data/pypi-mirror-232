import time

import click
import cv2
import numpy as np
from tqdm import tqdm

from mp_face_stylizer.sdk import FaceStylizer


@click.version_option(None, "-v", "--version")
@click.group()
def cli():
    print("hello from mp-face-stylizer!")


@cli.command()
@click.option("-i", "--img_path", help="Path to image")
@click.option("-m", "--model_path", help="Path to model")
@click.option("-o", "--out_path", help="Path to save path")
def img(img_path, model_path, out_path):
    t0 = time.time()
    sdk = FaceStylizer(model_path)

    img = cv2.imread(img_path)
    result_img = sdk.process(img)
    cv2.imwrite(out_path, result_img)
    t1 = time.time()
    print(f"fps: {1.0/(t1-t0):.2f}")


@cli.command()
@click.option("-i", "--in_video_path", help="Path to an video")
@click.option("-m", "--model_path", help="Path to model")
@click.option("-o", "--out_video_path", help="Path to save video path")
def video(in_video_path, model_path, out_video_path):
    sdk = FaceStylizer(model_path)

    cap = cv2.VideoCapture(in_video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    video_writer = cv2.VideoWriter(
        out_video_path, cv2.VideoWriter_fourcc(*"MP4V"), fps, (256, 256)
    )

    progress_bar = tqdm(total=total_frames, desc="Processing frames")

    t0 = time.time()
    while True:
        ret, img = cap.read()
        if ret:
            result_img = sdk.process(img)
            video_writer.write(result_img)
        else:
            break
        progress_bar.update(1)
    cap.release()
    t1 = time.time()
    print(f"fps: {1.0*total_frames/(t1-t0):.2f}")


@cli.command()
@click.option("-m", "--model_path", help="Path to model")
def camera(model_path):
    sdk = FaceStylizer(model_path)
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        t0 = time.time()
        ret, bgr_image = cap.read()
        result = sdk.process(bgr_image)
        if result is not None:
            h, w = result.shape[:2]
            bgr_image = cv2.resize(bgr_image, (w, h))
            comb = np.concatenate([bgr_image, result], axis=1)
            t1 = time.time()
            fps_str = f"fps: {1.0/(t1-t0):.2f}"
            cv2.putText(
                comb, fps_str, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1
            )
            cv2.imshow("camera", comb)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
