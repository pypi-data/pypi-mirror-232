# mp-face-stylizer
Python Face Stylizer Program based on MediaPipe

## How to run
Installing:
```
pip install mp-face-stylizer
```

Test with image:
```bash
mp_face_stylizer img -i /path/to/img -m /path/to/face_stylizer.task -o output.jpg
```

Test with video:
```bash
mp_face_stylizer video -i /path/to/video -m /path/to/face_stylizer.task -o output.mp4
```

Test with camera:
```bash
mp_face_stylizer camera -m /path/to/face_stylizer.task
```

## TODO
* [ ]. add model auto download pipeline
* [ ]. speedup running fps
+ [x]. show fps
