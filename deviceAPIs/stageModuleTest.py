from stage import Stage

from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QDoubleSpinBox, QSpinBox
from PySide6.QtCore import QTimer, Slot
from pylablib.devices import Thorlabs

base_size = 1                   # mm 값 입력
step_size = base_size / 1000    # 스테이지 전달용 수치 (m 단위로 전달)


def use_mm(value):
    return value/1000


def use_um(value):
    return value/1000000


class Window(QMainWindow):
    def __init__(self, ):
        super().__init__(None)

        self.stage = Stage(0)
        self.stage.setLimit(0, use_mm(5), use_mm(15))

        self.stage.errPositionLimit.connect(self.printErr)
        self.stage.errCannotDetect.connect(self.printErr)
        self.initUi()

    def initUi(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        ''' 위젯 선언 '''
        self.lbPosition = QLabel("position: ")
        self.lbStatus = QLabel("status: ")
        btnSetEnabled = QPushButton("enable/disable")

        lytMoveTo = QHBoxLayout()
        btnMoveTo = QPushButton("move to")
        lbMoveTo = QLabel("mm")
        self.sboxMoveTo = QDoubleSpinBox()
        self.sboxMoveTo.setDecimals(4)
        self.sboxMoveTo.setValue(self.stage.getPosition(0))
        lytMoveTo.addWidget(btnMoveTo)
        lytMoveTo.addWidget(self.sboxMoveTo)
        lytMoveTo.addWidget(lbMoveTo)

        # btnHome = QPushButton("home")

        btnJogPlus = QPushButton("jog +")
        btnJogMinus = QPushButton("jog -")
        btnDrivePlus = QPushButton("drive +")
        btnDriveMinus = QPushButton("drive -")

        ''' 클릭 이벤트 '''
        btnSetEnabled.clicked.connect(self.changeEnable)
        btnMoveTo.clicked.connect(self.moveTo)
        # btnHome.clicked.connect(self.home)

        btnJogPlus.clicked.connect(self.jogPlus)
        btnJogMinus.clicked.connect(self.jogMinus)
        btnDrivePlus.pressed.connect(self.drivePlus)
        btnDriveMinus.pressed.connect(self.driveMinus)
        btnDrivePlus.released.connect(self.stopDrive)
        btnDriveMinus.released.connect(self.stopDrive)

        ''' 레이아웃 추가 '''
        layout.addWidget(self.lbPosition)
        layout.addWidget(self.lbStatus)

        layout.addWidget(btnSetEnabled)
        layout.addLayout(lytMoveTo)
        # layout.addWidget(btnHome)

        layout.addWidget(btnJogPlus)
        layout.addWidget(btnJogMinus)
        layout.addWidget(btnDriveMinus)
        layout.addWidget(btnDrivePlus)
        self.setCentralWidget(central_widget)

    def changeEnable(self):
        if self.stage.isEnabled():
            self.stage.setEnabled(False)
        else:
            self.stage.setEnabled(True)

    def moveTo(self):
        target = self.sboxMoveTo.value()

        print(f"move to {target}[mm] = {target/1000}[m]")
        self.moveStartPosition = self.stage.getPosition(0)
        self.moveStartTime = datetime.now()

        formated = "{:.6f}".format(self.moveStartPosition * 1000)
        microFormated = "{:.3f}".format(self.moveStartPosition * 1000000)
        print(f"{datetime.now()} start: {formated}mm ({microFormated}um)")
        self.stage.move(0, target)

    def jogPlus(self):
        #print("jogPlus")
        self.stage.jog(0, "+")

    def jogMinus(self):
        #print("jogMinus")
        self.stage.jog(0, "-")

    def drivePlus(self):
        print("drivePlus")
        self.stage.driveStart(0, "+")

    def driveMinus(self):
        print("driveMinus")
        self.stage.driveStart(0, "-")

    def stopDrive(self):
        print("stopDrive")
        self.stage.driveStop(0)

    @Slot(str)
    def printErr(self, msg):
        print(msg)

if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
