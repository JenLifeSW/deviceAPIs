from deviceAPIs import Stage

from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QDoubleSpinBox, QSpinBox, QComboBox
from PySide6.QtCore import QTimer, Slot

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

        VSpacer1 = QVBoxLayout()
        VSpacer1.addSpacing(30)
        VSpacer2 = QVBoxLayout()
        VSpacer2.addSpacing(30)

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
        ## 드라이브 인터벌
        self.sboxSetInterval = QSpinBox()
        self.sboxSetInterval.setRange(1, 10000)
        self.sboxSetInterval.setValue(self.stage.getTimerInterval())
        btnSetInterval = QPushButton("set drive interval")
        btnSetInterval.clicked.connect(self.setInterval)
        lytSetInterval = QHBoxLayout()
        lytSetInterval.addWidget(self.sboxSetInterval)
        lytSetInterval.addWidget(btnSetInterval)
        layout.addLayout(lytSetInterval)

        layout.addLayout(VSpacer1)
        # 설정 UI
        ## 셋업 벨로시티(무브용?)
        lbSetupVelocityMin = QLabel("min velocity")
        lbSetupVelocityMax = QLabel("max velocity")
        lbSetupVelocityAcc = QLabel("acceleration")
        self.sboxSetupVelocityMin = QDoubleSpinBox()
        self.sboxSetupVelocityMax = QDoubleSpinBox()
        self.sboxSetupVelocityAcc = QDoubleSpinBox()
        self.sboxSetupVelocityMin.setDecimals(3)
        self.sboxSetupVelocityMax.setDecimals(3)
        self.sboxSetupVelocityAcc.setDecimals(3)

        self.comboSetupVelocityMin = QComboBox()
        self.comboSetupVelocityMax = QComboBox()
        self.comboSetupVelocityAcc = QComboBox()
        self.comboSetupVelocityMin.addItems(["mm", "um"])
        self.comboSetupVelocityMax.addItems(["mm", "um"])
        self.comboSetupVelocityAcc.addItems(["mm", "um"])
        self.setVelocityParams()
        btnSetupVelocity = QPushButton("setup Velocity")
        btnSetupVelocity.clicked.connect(self.setupVelocity)

        lytHSetupVelocityMin = QHBoxLayout()
        lytHSetupVelocityMax = QHBoxLayout()
        lytHSetupVelocityAcc = QHBoxLayout()
        lytVSetupVelocityMin = QVBoxLayout()
        lytVSetupVelocityMax = QVBoxLayout()
        lytVSetupVelocityAcc = QVBoxLayout()
        # lytVSetupVelocityMin.width

        lytHSetupVelocityMin.addWidget(self.sboxSetupVelocityMin)
        lytHSetupVelocityMin.addWidget(self.comboSetupVelocityMin)
        lytVSetupVelocityMin.addWidget(lbSetupVelocityMin)
        lytVSetupVelocityMin.addLayout(lytHSetupVelocityMin)

        lytHSetupVelocityMax.addWidget(self.sboxSetupVelocityMax)
        lytHSetupVelocityMax.addWidget(self.comboSetupVelocityMax)
        lytVSetupVelocityMax.addWidget(lbSetupVelocityMax)
        lytVSetupVelocityMax.addLayout(lytHSetupVelocityMax)

        lytHSetupVelocityAcc.addWidget(self.sboxSetupVelocityAcc)
        lytHSetupVelocityAcc.addWidget(self.comboSetupVelocityAcc)
        lytVSetupVelocityAcc.addWidget(lbSetupVelocityAcc)
        lytVSetupVelocityAcc.addLayout(lytHSetupVelocityAcc)

        lytSetupVelocity = QHBoxLayout()
        lytSetupVelocity.addLayout(lytVSetupVelocityMin)
        lytSetupVelocity.addLayout(lytVSetupVelocityMax)
        lytSetupVelocity.addLayout(lytVSetupVelocityAcc)
        lytSetupVelocity.addWidget(btnSetupVelocity)

        layout.addLayout(lytSetupVelocity)

        # 설정 UI
        ## 셋업 조그
        lbSetupJogSize = QLabel("size")
        lbSetupJogMin = QLabel("min velocity")
        lbSetupJogMax = QLabel("max velocity")
        lbSetupJogAcc = QLabel("acceleration")
        self.sboxSetupJogSize = QDoubleSpinBox()
        self.sboxSetupJogMin = QDoubleSpinBox()
        self.sboxSetupJogMax = QDoubleSpinBox()
        self.sboxSetupJogAcc = QDoubleSpinBox()
        self.sboxSetupJogSize.setDecimals(3)
        self.sboxSetupJogMin.setDecimals(3)
        self.sboxSetupJogMax.setDecimals(3)
        self.sboxSetupJogAcc.setDecimals(3)

        self.comboSetupJogSize = QComboBox()
        self.comboSetupJogMin = QComboBox()
        self.comboSetupJogMax = QComboBox()
        self.comboSetupJogAcc = QComboBox()
        self.comboSetupJogSize.addItems(["mm", "um"])
        self.comboSetupJogMin.addItems(["mm", "um"])
        self.comboSetupJogMax.addItems(["mm", "um"])
        self.comboSetupJogAcc.addItems(["mm", "um"])
        self.setJogParams()
        btnSetupJog = QPushButton("setup Jog")
        btnSetupJog.clicked.connect(self.setupJog)

        lytHSetupJogSize = QHBoxLayout()
        lytHSetupJogMin = QHBoxLayout()
        lytHSetupJogMax = QHBoxLayout()
        lytHSetupJogAcc = QHBoxLayout()
        lytVSetupJogSize = QVBoxLayout()
        lytVSetupJogMin = QVBoxLayout()
        lytVSetupJogMax = QVBoxLayout()
        lytVSetupJogAcc = QVBoxLayout()

        lytHSetupJogSize.addWidget(self.sboxSetupJogSize)
        lytHSetupJogSize.addWidget(self.comboSetupJogSize)
        lytVSetupJogSize.addWidget(lbSetupJogSize)
        lytVSetupJogSize.addLayout(lytHSetupJogSize)

        lytHSetupJogMin.addWidget(self.sboxSetupJogMin)
        lytHSetupJogMin.addWidget(self.comboSetupJogMin)
        lytVSetupJogMin.addWidget(lbSetupJogMin)
        lytVSetupJogMin.addLayout(lytHSetupJogMin)

        lytHSetupJogMax.addWidget(self.sboxSetupJogMax)
        lytHSetupJogMax.addWidget(self.comboSetupJogMax)
        lytVSetupJogMax.addWidget(lbSetupJogMax)
        lytVSetupJogMax.addLayout(lytHSetupJogMax)

        lytHSetupJogAcc.addWidget(self.sboxSetupJogAcc)
        lytHSetupJogAcc.addWidget(self.comboSetupJogAcc)
        lytVSetupJogAcc.addWidget(lbSetupJogAcc)
        lytVSetupJogAcc.addLayout(lytHSetupJogAcc)

        lytSetupJog = QHBoxLayout()
        lytSetupJog.addLayout(lytVSetupJogSize)
        lytSetupJog.addLayout(lytVSetupJogMin)
        lytSetupJog.addLayout(lytVSetupJogMax)
        lytSetupJog.addLayout(lytVSetupJogAcc)
        lytSetupJog.addWidget(btnSetupJog)

        layout.addLayout(lytSetupJog)
        layout.addLayout(VSpacer2)

        # 무브
        self.sboxMoveTo = QDoubleSpinBox()
        self.sboxMoveTo.setDecimals(4)
        self.sboxMoveTo.setRange(0, 50)
        self.sboxMoveTo.setValue(0.0)
        self.comboMoveTo = QComboBox()
        self.comboMoveTo.addItems(["mm", "um"])

        btnMoveTo = QPushButton("move to")
        btnStopMove = QPushButton("stop")
        btnMoveTo.clicked.connect(self.moveTo)
        btnStopMove.clicked.connect(self.stopMove)

        lytMoveTo = QHBoxLayout()
        lytMoveTo.addWidget(self.sboxMoveTo)
        lytMoveTo.addWidget(self.comboMoveTo)
        lytMoveTo.addWidget(btnMoveTo)
        lytMoveTo.addWidget(btnStopMove)

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

    def setInterval(self):
        interval = self.sboxSetInterval.value()
        self.stage.setTimerInterval(interval)

    def getUnitOfParam(self, value):
        if 1/(10**9) <= value:
            return value * (10 ** 3), "mm"
        else:
            return value * (10 ** 6), "um"

    def setVelocityParams(self):
        self.sboxSetupVelocityMin.setRange(0, 1000)
        self.sboxSetupVelocityMax.setRange(0, 1000)
        self.sboxSetupVelocityAcc.setRange(0, 1000)
        velocityParams = self.stage.getVelocityParameters(0)
        print(f"jogParams: {velocityParams}")
        minParam = self.getUnitOfParam(velocityParams[0])
        accParam = self.getUnitOfParam(velocityParams[1])
        maxParam = self.getUnitOfParam(velocityParams[2])

        self.sboxSetupVelocityMin.setValue(minParam[0])
        self.sboxSetupVelocityMax.setValue(maxParam[0])
        self.sboxSetupVelocityAcc.setValue(accParam[0])
        self.comboSetupVelocityMin.setCurrentText(minParam[1])
        self.comboSetupVelocityMax.setCurrentText(maxParam[1])
        self.comboSetupVelocityAcc.setCurrentText(accParam[1])

    def setJogParams(self):
        self.sboxSetupJogSize.setRange(0, 1000)
        self.sboxSetupJogMin.setRange(0, 1000)
        self.sboxSetupJogMax.setRange(0, 1000)
        self.sboxSetupJogAcc.setRange(0, 1000)
        jogParams = self.stage.getJogParameters(0)
        print(f"jogParams: {jogParams}")
        sizeParam = self.getUnitOfParam(jogParams[1])
        minParam = self.getUnitOfParam(jogParams[2])
        accParam = self.getUnitOfParam(jogParams[3])
        maxParam = self.getUnitOfParam(jogParams[4])

        self.sboxSetupJogSize.setValue(sizeParam[0])
        self.sboxSetupJogMin.setValue(minParam[0])
        self.sboxSetupJogMax.setValue(maxParam[0])
        self.sboxSetupJogAcc.setValue(accParam[0])
        self.comboSetupJogSize.setCurrentText(sizeParam[1])
        self.comboSetupJogMin.setCurrentText(minParam[1])
        self.comboSetupJogMax.setCurrentText(maxParam[1])
        self.comboSetupJogAcc.setCurrentText(accParam[1])

    def setupVelocity(self):
        minV = self.sboxSetupVelocityMin.value()
        maxV = self.sboxSetupVelocityMax.value()
        acc = self.sboxSetupVelocityAcc.value()
        unitOfMin = self.comboSetupVelocityMin.currentText()
        unitOfMax = self.comboSetupVelocityMax.currentText()
        unitOfAcc = self.comboSetupVelocityAcc.currentText()
        minV = use_mm(minV) if unitOfMin == "mm" else use_um(minV)
        maxV = use_mm(maxV) if unitOfMax == "mm" else use_um(maxV)
        acc = use_mm(acc) if unitOfAcc == "mm" else use_um(acc)

        velocityParams = self.stage.setupVelocity(0, minV, maxV, acc)
        velocityMinV = velocityParams[0] * (10 ** 6)
        velocityAcc = velocityParams[1] * (10 ** 6)
        velocityMaxV = velocityParams[2] * (10 ** 6)
        print(f"velocityParams: minV={velocityMinV}um, maxV={velocityMaxV}um, acc={velocityAcc}um")


    def setupJog(self):
        size = self.sboxSetupJogSize.value()
        minV = self.sboxSetupJogMin.value()
        maxV = self.sboxSetupJogMax.value()
        acc = self.sboxSetupJogAcc.value()
        unitOfSize = self.comboSetupJogSize.currentText()
        unitOfMin = self.comboSetupJogMin.currentText()
        unitOfMax = self.comboSetupJogMax.currentText()
        unitOfAcc = self.comboSetupJogAcc.currentText()
        size = use_mm(size) if unitOfSize == "mm" else use_um(size)
        minV = use_mm(minV) if unitOfMin == "mm" else use_um(minV)
        maxV = use_mm(maxV) if unitOfMax == "mm" else use_um(maxV)
        acc = use_mm(acc) if unitOfAcc == "mm" else use_um(acc)

        jogedParams = self.stage.setupJog(0, size, minV, maxV, acc)
        jogedSize = jogedParams[1] * (10 ** 6)
        jogedMinV = jogedParams[2] * (10 ** 6)
        jogedAcc = jogedParams[3] * (10 ** 6)
        jogedMaxV = jogedParams[4] * (10 ** 6)
        print(f"jogedParams: step_size={jogedSize}um, minV={jogedMinV}um, maxV={jogedMaxV}um, acc={jogedAcc}um")
        # p2d = self.stage.stage[0]._d2p
        # print(f"jogedParams: step_size={p2d(jogedSize, 'p')}, minV={p2d(jogedMinV, 'v')}, maxV={p2d(jogedMaxV, 'v')}, acc={p2d(jogedAcc, 'a')}")


    def moveTo(self):
        position = self.sboxMoveTo.value()
        unitOfPosition = self.comboMoveTo.currentText()
        if unitOfPosition == "mm":
            position = use_mm(position)
        else:
            position = use_um(position)

        print(f"move to {position}{unitOfPosition}")
        self.moveStartPosition = self.stage.getPosition(0)
        self.moveStartTime = datetime.now()

        formated = "{:.6f}".format(self.moveStartPosition * 1000)
        microFormated = "{:.3f}".format(self.moveStartPosition * 1000000)
        print(f"{datetime.now()} start: {formated}mm ({microFormated}um)")
        self.stage.move(0, position)
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
        status = self.stage.getStatus(0)
        status2 = self.stage.status[0]

        #print(f"status: {status}")
        self.lbStatus.setText(f"stage_status: {status}, module_status: {Status.get_name(status2)}")


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
