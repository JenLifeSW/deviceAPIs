import sys

import numpy as np
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget
from deviceAPIs.camera import Camera

class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.camera = Camera()
        self.resize(800, 600)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Camera Viewer")
        self.widget = QWidget(self)
        self.image_label = QLabel(self.widget)
        self.image_label.setScaledContents(True)
        self.image_label.resize(self.geometry().width(), self.geometry().height())
        # self.image_label.setAlignment(Qt.AlignCenter)

        # self.image_label2 = QLabel(self)
        # self.image_label2.setScaledContents(True)
        # self.image_label2.resize(self.geometry().width()/2, self.geometry().height())
        # self.image_label2.setAlignment(Qt.AlignCenter)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.widget)
        # self.layout.addWidget(self.image_label2)
        self.setLayout(self.layout)
        self.camera.signal_image.connect(lambda idx, image: self.update_image(idx, image))

        self.show_camera_list()

    def show_camera_list(self):
        camera_list = self.camera.get_available_camera_list()
        print(f"camera_list: {camera_list}")

        if len(camera_list) == 0:
            return
        self.connect_to_camera(camera_list[0])
        # self.connect_to_camera(camera_list[1])

    def connect_to_camera(self, idx):
        self.camera.connect_to_camera(idx)

    @Slot(int, np.ndarray)
    def update_image(self, idx, image):
        if image is not None:
            # NumPy 배열을 QImage로 변환
            qimage = QImage(image.data, image.shape[1], image.shape[0], (image.shape[1] * 24 + 31) // 32 * 4, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            # 이미지 표시
            if idx == 0:
                self.image_label.setPixmap(pixmap)
                self.image_label.resize(self.geometry().width(), self.geometry().height())
            # else:
            #     self.image_label2.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())
