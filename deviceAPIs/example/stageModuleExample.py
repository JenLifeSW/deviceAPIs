from deviceAPIs import Stage

from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QDoubleSpinBox, QSpinBox
from PySide6.QtCore import QTimer, Slot
from pylablib.devices import Thorlabs

from deviceAPIs.stage import Status

base_size = 1                   # mm 값 입력
step_size = base_size / 1000    # 스테이지 전달용 수치 (m 단위로 전달)


def use_mm(value):
    return value/1000


def use_um(value):
    return value/1000000


class Window(QMainWindow):
    positionTimer = QTimer()
    statusTimer = QTimer()

    def __init__(self, ):
        super().__init__(None)

        try:
            self.stage = Stage(1)
            self.initUi()
            self.positionTimer.timeout.connect(self.updatePosition)
            self.statusTimer.timeout.connect(self.updateStatus)

            self.positionTimer.start(100)
            self.statusTimer.start(100)

        except Exception as e:
            print(e)

    def initUi(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # 기본 UI
        self.lbPosition = QLabel("position: ")
        self.lbStatus = QLabel("status: ")
        btnSetEnabled = QPushButton("enable/disable")
        btnHome = QPushButton("home")
        btnSetEnabled.clicked.connect(self.changeEnable)
        btnHome.clicked.connect(lambda: self.home(0))

        layout.addWidget(self.lbPosition)
        layout.addWidget(self.lbStatus)
        layout.addWidget(btnSetEnabled)
        layout.addWidget(btnHome)

        # 설정 UI
        lytSetupJog = QHBoxLayout()
        lytSetInterval = QHBoxLayout()

        btnSetJogMM = QPushButton("set Jog mm")
        btnSetJogUM = QPushButton("set Jog um")
        btnSetInterval = QPushButton("set interval")

        self.sboxSetJog = QDoubleSpinBox()
        self.sboxSetInterval = QSpinBox()
        self.sboxSetJog.setDecimals(2)
        self.sboxSetJog.setValue(step_size)
        self.sboxSetInterval.setRange(1, 10000)
        self.sboxSetInterval.setValue(self.stage.getTimerInterval())
        lytSetupJog.addWidget(btnSetJogMM)
        lytSetupJog.addWidget(btnSetJogUM)
        lytSetupJog.addWidget(self.sboxSetJog)
        lytSetInterval.addWidget(btnSetInterval)
        lytSetInterval.addWidget(self.sboxSetInterval)

        btnSetJogMM.clicked.connect(self.setJogMM)
        btnSetJogUM.clicked.connect(self.setJogUM)
        btnSetInterval.clicked.connect(self.setInterval)

        layout.addLayout(lytSetupJog)
        layout.addLayout(lytSetInterval)

        # 무브
        lytMoveTo = QHBoxLayout()

        btnMoveTo = QPushButton("move to")
        btnStopMove = QPushButton("stop")
        self.sboxMoveTo = QDoubleSpinBox()
        lbMoveTo = QLabel("mm")
        self.sboxMoveTo.setDecimals(4)
        self.sboxMoveTo.setRange(-16.0, 30)
        self.sboxMoveTo.setValue(self.stage.getPosition(0))

        btnMoveTo.clicked.connect(self.moveTo)
        btnStopMove.clicked.connect(self.stopMove)
        lytMoveTo.addWidget(btnMoveTo)
        lytMoveTo.addWidget(btnStopMove)
        lytMoveTo.addWidget(self.sboxMoveTo)
        lytMoveTo.addWidget(lbMoveTo)

        layout.addLayout(lytMoveTo)

        # 조그 및 드라이브
        btnJogPlus = QPushButton("jog +")
        btnJogMinus = QPushButton("jog -")
        btnDrivePlus = QPushButton("drive +")
        btnDriveMinus = QPushButton("drive -")

        btnJogPlus.clicked.connect(self.jogPlus)
        btnJogMinus.clicked.connect(self.jogMinus)
        btnDrivePlus.pressed.connect(self.drivePlus)
        btnDriveMinus.pressed.connect(self.driveMinus)
        btnDrivePlus.released.connect(self.stopDrive)
        btnDriveMinus.released.connect(self.stopDrive)

        layout.addWidget(btnJogPlus)
        layout.addWidget(btnJogMinus)
        layout.addWidget(btnDrivePlus)
        layout.addWidget(btnDriveMinus)

        self.setCentralWidget(central_widget)

    def changeEnable(self):
        # if "enabled" not in self.stage.get_status():
        #     self.stage._enable_channel(True)
        # else:
        #     self.stage._enable_channel(False)
        self.stage.setEnabled(0, not self.stage.isEnabled(0))

    def setJogMM(self):
        jog_size = self.sboxSetJog.value()
        self.stage.setUpJog(0, use_mm(jog_size))

    def setJogUM(self):
        jog_size = self.sboxSetJog.value()
        self.stage.setUpJog(0, use_um(jog_size))

    def setInterval(self):
        interval = self.sboxSetInterval.value()
        self.stage.setTimerInterval(interval)

    def moveTo(self):
        target = self.sboxMoveTo.value()

        print(f"move to {target}[mm] = {target/1000}[m]")
        self.moveStartPosition = self.stage.getPosition(0)
        self.moveStartTime = datetime.now()

        formated = "{:.6f}".format(self.moveStartPosition * 1000)
        microFormated = "{:.3f}".format(self.moveStartPosition * 1000000)
        print(f"{datetime.now()} start: {formated}mm ({microFormated}um)")
        self.stage.move(0, target/1000)
        # self.checkMovingTimer.start(100)

    def stopMove(self):
        self.stage.stopMove(0, True)

    @Slot(int)
    def home(self, idx):             # 키네시스 프로필에 설정된 홈으로 이동하지만 비동기처리 되므로 move_to(0) 권장
        print("home")
        self.stage.home(idx)

    def jogPlus(self):
        #print("jogPlus")
        self.stage.jog(0, "+")

    def jogMinus(self):
        #print("jogMinus")
        self.stage.jog(0, "-")

    def drivePlus(self):
        print("drivePlus")
        self.stage.driveStart(0, "+")

    def printDriveVelocity(self):
        position = self.stage.getPosition(0)
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        # dt = datetime.now()
        # insDiff = position - self.previousPosition
        # insTDiff = dt.timestamp() - self.previousTime.timestamp()
        # print(f"{datetime.now()} moved: {formated}mm ({microFormated}um) 순간속도:{round((insDiff*1000000/insTDiff), 4)}um/sec")
        #
        # self.previousPosition = position
        # self.previousTime = dt

    def driveMinus(self):
        print("driveMinus")
        self.stage.driveStart(0, "-")

    def stopDrive(self):
        print("stopDrive")
        self.stage.driveStop(0)

    def updatePosition(self):
        position = self.stage.getPosition(0)
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        self.lbPosition.setText(f"position: {formated}mm ({microFormated}um)")

    def updateStatus(self):
        status = self.stage.stage[0].get_status()
        status2 = self.stage.status[0]

        #print(f"status: {status}")
        self.lbStatus.setText(f"stage_status: {status}, module_status: {Status.get_name(status2)}")


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
