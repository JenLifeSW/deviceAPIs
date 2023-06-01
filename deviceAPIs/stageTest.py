from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDoubleSpinBox
from PySide6.QtCore import QTimer
from pylablib.devices import Thorlabs

base_size = 1                   # mm 값 입력
step_size = base_size / 1000    # 스테이지 전달용 수치 (m 단위로 전달)


class Window(QMainWindow):
    positionTimer = QTimer()
    statusTimer = QTimer()
    drivePlusTimer = QTimer()
    driveMinusTimer = QTimer()

    def __init__(self, ):
        super().__init__(None)

        if self.initDevice():
            self.initUi()
            self.positionTimer.timeout.connect(self.updatePosition)
            self.statusTimer.timeout.connect(self.updateStatus)
            self.drivePlusTimer.timeout.connect(self.jogPlus)
            self.driveMinusTimer.timeout.connect(self.jogMinus)

            self.positionTimer.start(100)
            self.statusTimer.start(100)

    def initDevice(self):
        devices = Thorlabs.kinesis.list_kinesis_devices()
        if len(devices) < 1:
            print("스테이지를 찾지 못함")
            return False
        print("스테이지 연결")

        self.stage = Thorlabs.KinesisMotor(devices[0][0], "MTS50-Z8")
        self.stage.setup_velocity(min_velocity=0.0001, max_velocity=0.01)
        self.stage.setup_jog(step_size=step_size)
        return True

    def initUi(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        ''' 위젯 선언 '''
        self.lbPosition = QLabel("position: ")
        self.lbStatus = QLabel("status: ")

        btnSetEnabled = QPushButton("enable/disable")
        lytMoveTo = QHBoxLayout()
        btnMoveTo = QPushButton("move to")
        self.sboxMoveTo = QDoubleSpinBox()
        self.sboxMoveTo.setDecimals(3)
        lbMoveTo = QLabel("mm")
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
        if "enabled" not in self.stage.get_status():
            self.stage._enable_channel(True)
        else:
            self.stage._enable_channel(False)

    def moveTo(self):
        target = self.sboxMoveTo.value()
        print(f"move to {target}[mm] = {target/1000}[m]")
        self.stage.move_to(target/1000)

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
        self.drivePlusTimer.start(10)

    def driveMinus(self):
        print("driveMinus")
        self.driveMinusTimer.start(10)

    def stopDrive(self):
        print("stopDrive")
        self.drivePlusTimer.stop()
        self.driveMinusTimer.stop()

    def updatePosition(self):
        position = self.stage.get_position()
        #print(f"position: {position}")
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        self.lbPosition.setText(f"position: {formated}mm ({microFormated}um)")

    def updateStatus(self):
        status = self.stage.get_status()
        #print(f"status: {status}")
        self.lbStatus.setText(f"status: {status}")


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
