import sys

import numpy as np
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QImage, QPixmap, QScreen
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from deviceAPIs.camera import Camera

class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.camera = Camera()
        self.setFixedSize(800, 600)
        # qtRectangle = self.frameGeometry()
        # self.move(qtRectangle.topLeft())
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Camera Viewer")
        # self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)
        self.image_label.resize(self.geometry().width(), self.geometry().height())
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)
        self.camera.signal_image.connect(lambda idx, image: self.update_image(idx, image))

        self.show_camera_list()

    def show_camera_list(self):
        camera_list = self.camera.get_available_camera_list()
        print(f"camera_list: {camera_list}")

        if len(camera_list) == 0:
            return
        self.connect_to_camera(camera_list[0])

    def connect_to_camera(self, idx):
        self.camera.connect_to_camera(idx)

    @Slot(int, np.ndarray)
    def update_image(self, idx, image):
        if image is not None:
            # NumPy 배열을 QImage로 변환
            qimage = QImage(image.data, image.shape[1], image.shape[0], (image.shape[1] * 24 + 31) // 32 * 4, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            # 이미지 표시
            self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())
