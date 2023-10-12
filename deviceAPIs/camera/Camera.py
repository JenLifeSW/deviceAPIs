import numpy as np
from PySide6.QtCore import QObject, Signal, Slot
from deviceAPIs.camera import toupcam
from deviceAPIs.camera.CameraUnit import ToupcamUnit, CVUnit
import cv2 as cv2


class Camera(QObject):
    signal_image = Signal(int, np.ndarray)
    exception = Signal(str)

    using_cameras = []

    def __init__(self):
        super().__init__()

    def get_toupcam_list(self):
        toupcam_units = []

        toupcams = toupcam.Toupcam.EnumV2()
        for cam in toupcams:
            camera_available = True
            toupcam_unit = ToupcamUnit(cam.displayname, cam.id, cam.model)

            for using_camera in self.using_cameras:
                if using_camera.is_same(toupcam_unit):
                    print("is using")
                    camera_available = False
                    break
            if camera_available:
                print("append camera")
                toupcam_units.append(toupcam_unit)

        return toupcam_units

    def get_cvcam_list(self):
        cvcam_units = []
        non_working_ports = 0
        dev_port = 0
        while non_working_ports < 4:  # if there are more than 3 non working ports stop the testing.
            camera = cv2.VideoCapture(dev_port)

            if not camera.isOpened():
                non_working_ports += 1
                dev_port += 1
                continue
            is_reading, img = camera.read()
            if not is_reading:
                non_working_ports += 1
                dev_port += 1
                continue
            cvcam_unit = CVUnit(cam_id=dev_port)
            cvcam_units.append(cvcam_unit)
            dev_port += 1
        return cvcam_units

    def get_available_camera_list(self):
        toupcam_units = self.get_toupcam_list()
        cvcam_units = self.get_cvcam_list()
        camera_units = toupcam_units + cvcam_units

        return camera_units

    def connect_to_camera(self, camera_unit):
        if camera_unit in self.using_cameras:
            print("this camera is using")
            return

        idx = len(self.using_cameras)
        self.using_cameras.append(camera_unit)
        self.using_cameras[idx].connect_to_camera()
        self.using_cameras[idx].signal_image.connect(lambda image: self.on_image_signal(idx, image))

    def disconnect_to_camera(self, idx):
        if self.using_cameras[idx] is None:
            print("{idx} camera is already closed")
            return

        self.using_cameras[idx].signal_image.disconnect()
        self.using_cameras[idx].close()
        self.using_cameras[idx] = None

    @Slot(int, np.ndarray)
    def on_image_signal(self, idx, image):
        self.signal_image.emit(idx, image)
