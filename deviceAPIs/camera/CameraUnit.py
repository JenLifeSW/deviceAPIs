import sys

import cv2
import numpy as np

from PySide6.QtCore import QObject, Signal, Slot, Qt, QThread

from deviceAPIs.camera import toupcam

# MAX_RESOLUTION = [10240, 4320]


class CamType:
    DEFAULT = 0
    TOUPCAM = 1
    CV = 2

    @classmethod
    def get_name(cls, num):
        cam_type = {
            cls.DEFAULT: "default",
            cls.TOUPCAM: "toupcam",
            cls.CV: "CV cam",
        }
        return cam_type.get(num, "UNKNOWN")


class CameraUnit(QThread):
    signal_image = Signal(np.ndarray)
    exception = Signal(str)

    def __init__(self, name=None, cam_id=None, model=None):
        super().__init__()
        self.type = CamType.DEFAULT
        self.name = name
        self.cam_id = cam_id
        self.model = model
        self.cam = None
        self.buf = None  # video buffer
        self.width = 0  # video width
        self.height = 0  # video height

    def run(self):
        pass

    def is_same(self, camera_unit):
        pass

    def connect_to_camera(self):
        pass

    def close(self, event):
        pass


class ToupcamUnit(CameraUnit):
    def __init__(self, name, cam_id, model):
        super().__init__(name, cam_id, model)
        self.type = CamType.TOUPCAM

    def run(self):
        pass

    def is_same(self, camera_unit):
        return self.cam_id == camera_unit.cam_id and self.name == camera_unit.name

    def connect_to_camera(self):
        try:
            self.cam = toupcam.Toupcam.Open(self.cam_id)
            print(f"connected {'='*10}")
        except toupcam.HRESULTException as e:
            self.exception.emit(f"failed to open camera: {e}")
        else:
            self.w, self.h = self.cam.get_Size()
            print(f"size: {self.cam.get_Size()}")
            bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
            self.buf = bytes(bufsize)
            print(self.buf.__sizeof__())
            try:
                if sys.platform == "win32":
                    self.cam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0)
                    self.cam.StartPullModeWithCallback(self.cameraCallback, self)
            except toupcam.HRESULTException as e:
                self.exception.emit(f"failed to open camera: {e}")

    def close(self, event):
        if self.cam is not None:
            self.cam.Close()
            self.cam = None

    # the vast majority of callbacks come from toupcam.dll/so/dylib internal threads, so we use qt signal to post this event to the UI thread
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                ctx.cam.PullImageV2(ctx.buf, 24, None)
            except toupcam.HRESULTException as e:
                ctx.exception.emit(f"pull image failed: {e}")
            else:
                img_np = np.frombuffer(ctx.buf, dtype=np.uint8).reshape((ctx.height, ctx.width, 3))
                ctx.signal_image.emit(img_np)

    def change_auto_exposure(self, state):
        if self.cam is not None:
            self.cam.put_AutoExpoEnable(state == Qt.Checked)


class CVUnit(CameraUnit):
    def __init__(self, cam_id):
        super().__init__(cam_id=cam_id)
        self.type = CamType.CV

    def run(self):
        while True:
            ret, frame = self.cam.read()
            self.signal_image.emit(frame)

    def is_same(self, camera_unit):
        pass

    def connect_to_camera(self):
        self.cam = cv2.VideoCapture(self.cam_id)
        if not self.cam.isOpened():
            self.exception.emit(f"failed to open cv2 camera")
            return

        # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, MAX_RESOLUTION[0])
        # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, MAX_RESOLUTION[1])
        #
        # _, frame = self.cam.read()
        # dim = frame.shape[:1]
        # self.width = dim[1]
        # self.height = dim[0]
        #
        # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.start()

    def close(self, event):
        if not self.cam.isOpened():
            return
        self.cam.release()
        self.cam = None
