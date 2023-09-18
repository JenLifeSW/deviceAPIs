from deviceAPIs.v2 import Stage
from deviceAPIs.v2.stageControlUnit import Condition

from datetime import datetime

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QDoubleSpinBox, QSpinBox, QComboBox
from PySide6.QtCore import QTimer, Slot, Qt

updateInterval = 100

def use_mm(value):
    return value/1000


def use_um(value):
    return value/1000000


class Window(QMainWindow):
    positionTimer = QTimer()
    statusTimer = QTimer()
    buttonConnected = False

    def __init__(self, ):
        super().__init__(None)

        try:
            self.stage = Stage()
            self.initUI()
            self.stage.connectedSignal.connect(self.onConnectedSignal)
            self.positionTimer.timeout.connect(self.updatePositionLabel)
            self.statusTimer.timeout.connect(self.updateStatusLabel)

        except Exception as e:
            print(e)

    def initUI(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        VSpacer1 = QVBoxLayout()
        VSpacer1.addSpacing(30)
        VSpacer2 = QVBoxLayout()
        VSpacer2.addSpacing(30)

        # 기본 UI
        self.lbConnected = QLabel("connected: False")
        self.lbConnected.setAlignment(Qt.AlignCenter)
        font = self.lbConnected.font()
        font.setPointSize(16)
        self.lbConnected.setFont(font)
        self.lbPosition = QLabel("position: ")
        self.lbStatus = QLabel("status: ")
        self.btnSetEnabled = QPushButton("enable/disable")
        self.btnHome = QPushButton("home")

        layout.addWidget(self.lbConnected)
        layout.addWidget(self.lbPosition)
        layout.addWidget(self.lbStatus)
        layout.addWidget(self.btnSetEnabled)
        layout.addWidget(self.btnHome)
        self.btnGetParams = QPushButton("get parameters")
        layout.addWidget(self.btnGetParams)

        # 설정 UI
        ## 드라이브 인터벌
        self.sboxSetInterval = QSpinBox()
        self.sboxSetInterval.setRange(1, 10000)
        self.btnSetInterval = QPushButton("set drive interval")
        lytSetInterval = QHBoxLayout()
        lytSetInterval.addWidget(self.sboxSetInterval)
        lytSetInterval.addWidget(self.btnSetInterval)
        layout.addLayout(lytSetInterval)

        layout.addLayout(VSpacer1)
        # 설정 UI
        ## 셋업 벨로시티(무브용)
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
        self.btnSetupVelocity = QPushButton("setup velocity")

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
        lytSetupVelocity.addWidget(self.btnSetupVelocity)

        layout.addLayout(lytSetupVelocity)

        # 셋업 UI
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
        self.btnSetupJog = QPushButton("setup Jog")

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
        lytSetupJog.addWidget(self.btnSetupJog)

        layout.addLayout(lytSetupJog)
        layout.addLayout(VSpacer2)

        # 무브
        self.sboxMoveTo = QDoubleSpinBox()
        self.sboxMoveTo.setDecimals(4)
        self.sboxMoveTo.setRange(0, 50)
        self.sboxMoveTo.setValue(0.0)
        self.comboMoveTo = QComboBox()
        self.comboMoveTo.addItems(["mm", "um"])

        self.btnMoveTo = QPushButton("move to")
        self.btnStopMove = QPushButton("stop")

        lytMoveTo = QHBoxLayout()
        lytMoveTo.addWidget(self.sboxMoveTo)
        lytMoveTo.addWidget(self.comboMoveTo)
        lytMoveTo.addWidget(self.btnMoveTo)
        lytMoveTo.addWidget(self.btnStopMove)

        layout.addLayout(lytMoveTo)

        # 조그 및 드라이브
        self.btnJogPlus = QPushButton("jog +")
        self.btnJogMinus = QPushButton("jog -")
        self.btnDrivePlus = QPushButton("drive +")
        self.btnDriveMinus = QPushButton("drive -")

        layout.addWidget(self.btnJogPlus)
        layout.addWidget(self.btnJogMinus)
        layout.addWidget(self.btnDrivePlus)
        layout.addWidget(self.btnDriveMinus)

        self.setCentralWidget(central_widget)

    def setView(self):
        self.sboxSetInterval.setValue(self.stage.getTimerInterval(0))
        self.setVelocityParams()
        self.setJogParams()

    def connectButtonAction(self):
        self.buttonConnected = True

        self.btnGetParams.clicked.connect(self.setView)
        # 기본 버튼
        self.btnSetEnabled.clicked.connect(self.changeEnable)
        self.btnHome.clicked.connect(self.home)

        # 셋업
        self.btnSetInterval.clicked.connect(self.setInterval)
        self.btnSetupVelocity.clicked.connect(self.setupVelocity)
        self.btnSetupJog.clicked.connect(self.setupJog)

        # 이동
        self.btnJogPlus.clicked.connect(self.jogPlus)
        self.btnJogMinus.clicked.connect(self.jogMinus)
        self.btnDrivePlus.pressed.connect(self.drivePlus)
        self.btnDriveMinus.pressed.connect(self.driveMinus)
        self.btnDrivePlus.released.connect(self.stopDrive)
        self.btnDriveMinus.released.connect(self.stopDrive)

        self.btnMoveTo.clicked.connect(self.moveTo)
        self.btnStopMove.clicked.connect(self.stopMove)

    @Slot(int, bool)
    def onConnectedSignal(self, _, isConnected):
        self.lbConnected.setText(f"connected: {isConnected}")
        if isConnected:
            self.positionTimer.start(updateInterval)
            self.statusTimer.start(updateInterval)
            self.setView()
            if not self.buttonConnected:
                self.connectButtonAction()

            self.stage.homedSignal.connect(lambda idx: print(f"[{idx}] homed"))
            self.stage.stoppedSignal.connect(lambda idx, position: print(f"[{idx}] stopped: {position}"))
            self.stage.movedSignal.connect(lambda idx, position: print(f"[{idx}] moved: {position}"))

        else:
            self.statusTimer.stop()
            self.positionTimer.stop()
            self.stage.homedSignal.disconnect()
            self.stage.stoppedSignal.disconnect()
            self.stage.movedSignal.disconnect()

    def updatePositionLabel(self):
        position = self.stage.getPosition(0)
        formated = "{:.6f}".format(position * 1000)
        microFormated = "{:.3f}".format(position * 1000000)
        self.lbPosition.setText(f"position: {formated}mm ({microFormated}um)")

    def updateStatusLabel(self):
        status = self.stage.getStatus(0)
        condition = self.stage.getCondition(0)
        self.lbStatus.setText(f"stage_status: {status}, condition: {Condition.get_name(condition)}")

    def changeEnable(self):
        self.stage.toggleEnabled(0)

    def setInterval(self):
        interval = self.sboxSetInterval.value()
        self.stage.setTimerInterval(0, interval)

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
        self.stage.stopMove(0)

    def home(self):
        self.stage.home(0, True)

    def jogPlus(self):
        self.stage.jog(0, "+")

    def jogMinus(self):
        self.stage.jog(0, "-")

    def drivePlus(self):
        self.stage.startDrive(0, "+")

    def driveMinus(self):
        self.stage.startDrive(0, "-")

    def stopDrive(self):
        self.stage.stopDrive(0)


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
