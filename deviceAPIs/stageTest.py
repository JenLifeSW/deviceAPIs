from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QDoubleSpinBox, QSpinBox
from PySide6.QtCore import QTimer
from pylablib.devices import Thorlabs

base_size = 1                   # mm 값 입력
step_size = base_size / 1000    # 스테이지 전달용 수치 (m 단위로 전달)


def use_mm(value):
    return value/1000


def use_um(value):
    return value/1000000


class Window(QMainWindow):
    positionTimer = QTimer()
    statusTimer = QTimer()
    drivePlusTimer = QTimer()
    driveMinusTimer = QTimer()
    checkMovingTimer = QTimer()

    isMoving = False
    moveStartPosition = 0.0
    moveStartTime = datetime.now()
    previousPosition = 0.0
    previousTime = datetime.now()
    driveInterval = 303

    def __init__(self, ):
        super().__init__(None)

        if self.initDevice():
            self.initUi()
            self.positionTimer.timeout.connect(self.updatePosition)
            self.statusTimer.timeout.connect(self.updateStatus)
            self.drivePlusTimer.timeout.connect(self.jogPlus)
            self.driveMinusTimer.timeout.connect(self.jogMinus)
            self.checkMovingTimer.timeout.connect(self.checkMoving)
            self.drivePlusTimer.timeout.connect(self.printDriveVelocity)
            self.driveMinusTimer.timeout.connect(self.printDriveVelocity)

            self.positionTimer.start(100)
            self.statusTimer.start(100)

    def initDevice(self):
        devices = Thorlabs.kinesis.list_kinesis_devices()
        if len(devices) < 1:
            print("스테이지를 찾지 못함")
            return False
        print("스테이지 연결")

        self.stage = Thorlabs.KinesisMotor(devices[0][0], "MTS50-Z8")
        # self.stage.setup_velocity(min_velocity=0.0000007, max_velocity=0.0000007
        self.stage.setup_velocity(min_velocity=use_um(0.6), max_velocity=use_um(0.6))
        self.stage.setup_jog(step_size=use_um(0.1))
        return True

    def initUi(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        ''' 위젯 선언 '''
        self.lbPosition = QLabel("position: ")
        self.lbStatus = QLabel("status: ")
        btnSetEnabled = QPushButton("enable/disable")

        lytMoveTo = QHBoxLayout()
        lytSetupJog = QHBoxLayout()
        lytSetInterval = QHBoxLayout()

        btnMoveTo = QPushButton("move to")
        lbMoveTo = QLabel("mm")
        self.sboxMoveTo = QDoubleSpinBox()
        self.sboxMoveTo.setDecimals(4)
        self.sboxMoveTo.setValue(self.stage.get_position())
        lytMoveTo.addWidget(btnMoveTo)
        lytMoveTo.addWidget(self.sboxMoveTo)
        lytMoveTo.addWidget(lbMoveTo)

        btnSetJogMM = QPushButton("set Jog mm")
        btnSetJogUM = QPushButton("set Jog um")
        btnSetInterval = QPushButton("set interval")

        self.sboxSetJog = QDoubleSpinBox()
        self.sboxSetInterval = QSpinBox()
        self.sboxSetJog.setDecimals(2)
        self.sboxSetJog.setValue(step_size)
        self.sboxSetInterval.setRange(1, 10000)
        self.sboxSetInterval.setValue(self.driveInterval)
        lytSetupJog.addWidget(btnSetJogMM)
        lytSetupJog.addWidget(btnSetJogUM)
        lytSetupJog.addWidget(self.sboxSetJog)
        lytSetInterval.addWidget(btnSetInterval)
        lytSetInterval.addWidget(self.sboxSetInterval)

        # btnHome = QPushButton("home")

        btnJogPlus = QPushButton("jog +")
        btnJogMinus = QPushButton("jog -")
        btnDrivePlus = QPushButton("drive +")
        btnDriveMinus = QPushButton("drive -")

        ''' 클릭 이벤트 '''
        btnSetEnabled.clicked.connect(self.changeEnable)
        btnMoveTo.clicked.connect(self.moveTo)
        btnSetJogMM.clicked.connect(self.setJogMM)
        btnSetJogUM.clicked.connect(self.setJogUM)
        btnSetInterval.clicked.connect(self.setInterval)
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
        layout.addLayout(lytSetupJog)
        layout.addLayout(lytSetInterval)
        # layout.addWidget(btnHome)

        layout.addWidget(btnJogPlus)
        layout.addWidget(btnJogMinus)
        layout.addWidget(btnDriveMinus)
        layout.addWidget(btnDrivePlus)
        self.setCentralWidget(central_widget)

    def changeEnable(self):
        if "enabled" not in self.stage.get_status():
            self.stage._enable_channel(True)
        else:
            self.stage._enable_channel(False)

    def setJogMM(self):
        jog_size = self.sboxSetJog.value()
        self.stage.setup_jog(step_size=use_mm(jog_size))

    def setJogUM(self):
        jog_size = self.sboxSetJog.value()
        self.stage.setup_jog(step_size=use_um(jog_size))

    def setInterval(self):
        interval = self.sboxSetInterval.value()
        self.driveInterval = interval

    def moveTo(self):
        target = self.sboxMoveTo.value()

        print(f"move to {target}[mm] = {target/1000}[m]")
        self.moveStartPosition = self.stage.get_position()
        self.moveStartTime = datetime.now()

        formated = "{:.6f}".format(self.moveStartPosition * 1000)
        microFormated = "{:.3f}".format(self.moveStartPosition * 1000000)
        print(f"{datetime.now()} start: {formated}mm ({microFormated}um)")
        self.stage.move_to(target/1000)
        self.checkMovingTimer.start(100)

    # def home(self):             # 키네시스 프로필에 설정된 홈으로 이동하지만 비동기처리 되므로 move_to(0) 권장
    #     print("home")
    #     self.stage.home(force=True)

    def jogPlus(self):
        #print("jogPlus")
        self.stage.jog("+", kind="builtin")

    def jogMinus(self):
        #print("jogMinus")
        self.stage.jog("-", kind="builtin")

    def drivePlus(self):
        print("drivePlus")
        self.drivePlusTimer.start(self.driveInterval)

    def printDriveVelocity(self):
        position = self.stage.get_position()
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        dt = datetime.now()
        insDiff = position - self.previousPosition
        insTDiff = dt.timestamp() - self.previousTime.timestamp()
        print(f"{datetime.now()} moved: {formated}mm ({microFormated}um) 순간속도:{round((insDiff*1000000/insTDiff), 4)}um/sec")

        self.previousPosition = position
        self.previousTime = dt

    def driveMinus(self):
        print("driveMinus")
        self.driveMinusTimer.start(self.driveInterval)

    def stopDrive(self):
        print("stopDrive")
        self.drivePlusTimer.stop()
        self.driveMinusTimer.stop()

    def updatePosition(self):
        position = self.stage.get_position()
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        self.lbPosition.setText(f"position: {formated}mm ({microFormated}um)")

    def updateStatus(self):
        status = self.stage.get_status()
        #print(f"status: {status}")
        self.lbStatus.setText(f"status: {status}")

    def checkMoving(self):
        status = self.stage.get_status()
        if (
                "moving_fw" not in status and
                "moving_bk" not in status and
                "jogging_fw" not in status and
                "jogging_bk" not in status
        ):
            self.checkMovingTimer.stop()
            self.isMoving = False
        position = self.stage.get_position()
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        dt = datetime.now()
        diff = position - self.moveStartPosition
        tDiff = (dt.timestamp() - self.moveStartTime.timestamp())

        insDiff = position - self.previousPosition
        insTDiff = dt.timestamp() - self.previousTime.timestamp()
        print(f"{datetime.now()} moved: {formated}mm ({microFormated}um) {round((diff*1000000/tDiff), 4)}um/sec 순간속도:{round((insDiff*1000000/insTDiff), 4)}um/sec")

        self.previousPosition = position
        self.previousTime = dt



if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
