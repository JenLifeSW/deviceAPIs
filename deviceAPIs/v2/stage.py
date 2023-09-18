from PySide6.QtCore import QObject, QTimer, Signal, Slot
from pylablib.devices import Thorlabs

from deviceAPIs.v2.stageControlUnit import StageControlUnit

TAG = "stage"


class Stage(QObject):
    requireStages = 1
    ignore = False
    serials = []
    disconnectedStageIdx = []
    stages = []

    errorCanNotConnectToDevice = Signal(int)
    errorPositionLimit = Signal(int, str)

    connectedSignal = Signal(int, bool)
    homedSignal = Signal(int)
    stoppingSignal = Signal(int)
    stoppedSignal = Signal(int, float)
    movedSignal = Signal(int, float)

    tryToConnectTimer = QTimer()
    tryInterval = 1000

    def __init__(self, requireStages=1, ignore=False):
        """

        :param requireStages: 연결할 스테이지 갯수
        :param ignore: 인식된 스테이지가 requireStages보다 작을 때 무시하고 연결할지 여부
        """

        super().__init__()
        self.requireStages = requireStages
        self.ignore = ignore
        for _ in range(requireStages):
            self.stages.append(None)

        self.tryToConnectTimer.timeout.connect(self.checkConnect)
        self.tryToConnectTimer.start(self.tryInterval)

    def close(self):
        for stage in self.stages:
            if stage:
                stage.close()

    def _getStage(self, idx):
        stage = self.stages[idx]
        if idx not in self.disconnectedStageIdx:
            try:
                stage.getStatus()
                return stage
            except Exception as e:
                print(f"An error occurred : {e}")
                self.addDisconnectedStageIdx(idx)
                return

    def checkConnect(self):
        METHOD = "[checkConnect]"
        devices = Thorlabs.kinesis.list_kinesis_devices()

        # print("checkConnect")
        print(f"{TAG}{METHOD} disconnected stage: {self.disconnectedStageIdx}, len(devices): {len(devices)}")
        # 새로 인식된 스테이지가 있다면 시리얼 번호를 저장하고 disConnectedStage에 추가합니다.
        if len(self.serials) < len(devices):
            for device in devices:
                print(f"{TAG}{METHOD} device 추가: [{len(self.serials)}] {device}")
                serial = device[0]
                if serial not in self.serials:
                    self.disconnectedStageIdx.append(len(self.serials))
                    self.serials.append(serial)

        # 연결되지 않은 스테이지가 없다면 메서드를 반환합니다.
        if all(stage is not None for stage in self.stages):
            print(f"{TAG}{METHOD} stages: {self.stages}")
            self.tryToConnectTimer.stop()
            return
        if len(devices) != 0 and len(self.disconnectedStageIdx) == 0:
            print(f"{TAG}{METHOD} 추가 스테이지 없음")
            self.tryToConnectTimer.stop()
            return

        # 연결되지 않은 스테이지에 연결을 시도하고 연결되었다면 해당 리스트에서 제거합니다.
        connectedStageIdx = []
        for idx in self.disconnectedStageIdx:
            serial = self.serials[idx]
            print(f"{TAG}{METHOD} [{idx}] 스테이지 연결시도: {serial}")
            try:
                self.stages[idx] = StageControlUnit(serial)
                self.stages[idx].initedSignal.connect(lambda: self.onInitedSignal(idx))
                connectedStageIdx.append(idx)

            except Exception as e:
                print(f"[stage#{serial}] KinesisMotor에 연결할 수 없습니다.", e)
                self.errorCanNotConnectToDevice.emit(serial)

        self.disconnectedStageIdx = [idx for idx in self.disconnectedStageIdx if idx not in connectedStageIdx]

    @Slot(int)
    def onInitedSignal(self, idx):
        print(f"stage#{idx} inited")
        self.connectSignal(idx)

    def addDisconnectedStageIdx(self, idx):
        if idx in self.disconnectedStageIdx:
            return
        print(f"stage[addDisConnectedStage] [{idx}], discon: {self.disconnectedStageIdx}")
        self.disconnectedStageIdx.append(idx)
        self.disconnectSignal(idx)
        self.stages[idx].close()
        self.stages[idx].deleteLater()
        self.stages[idx] = None
        self.connectedSignal.emit(idx, False)
        self.tryToConnectTimer.start(self.tryInterval)

    def connectSignal(self, idx):
        stage = self._getStage(idx)
        stage.errorPositionLimit.connect(lambda msg: self.errorPositionLimit.emit(idx, msg))
        stage.homedSignal.connect(lambda: self.homedSignal.emit(idx))
        stage.stoppingSignal.connect(lambda: self.stoppingSignal.emit(idx))
        stage.stoppedSignal.connect(lambda position: self.stoppedSignal.emit(idx, position))
        stage.stageMovedSignal.connect(lambda position: self.movedSignal.emit(idx, position))
        self.connectedSignal.emit(idx, True)

    def disconnectSignal(self, idx):
        stage = self.stages[idx]
        stage.errorPositionLimit.disconnect()
        stage.homedSignal.disconnect()
        stage.stoppingSignal.disconnect()
        stage.stoppedSignal.disconnect()
        stage.stageMovedSignal.disconnect()

    def getTimerInterval(self, idx):
        try:
            return self._getStage(idx).getTimerInterval()
        except Exception as e:
            return 100

    def setTimerInterval(self, idx, interval):
        try:
            self._getStage(idx).setTimerInteval(interval)
        except Exception as e:
            return

    def getCondition(self, idx):
        try:
            return self._getStage(idx).getCondition()
        except Exception as e:
            return -1

    def getStatus(self, idx):
        try:
            return self._getStage(idx).getStatus()
        except Exception as e:
            return [-1]

    def isHomed(self, idx):
        return "homed" in self.getStatus(idx)

    def setLimit(self, idx, bottom, top):
        try:
            self._getStage(idx).setLimit(bottom, top)
        except Exception as e:
            return

    def getJogParameters(self, idx):
        try:
            return self._getStage(idx).getJogParameters()
        except Exception as e:
            return [-1, -1, -1, -1, -1, -1]

    def getVelocityParameters(self, idx):
        try:
            return self._getStage(idx).getVelocityParameters()
        except Exception as e:
            return [-1, -1, -1]

    def setupJog(self, idx, size=None, minVelocity=None, maxVelocity=None, acceleration=None):
        try:
            return self._getStage(idx).setupJog(size=size, minVelocity=minVelocity, maxVelocity=maxVelocity, acceleration=acceleration)
        except Exception as e:
            return [-1, -1, -1, -1, -1, -1]

    def setupVelocity(self, idx, minVelocity=None, maxVelocity=None, acceleration=None):
        try:
            return self._getStage(idx).setupVelocity(minVelocity=minVelocity, maxVelocity=maxVelocity, acceleration=acceleration)
        except Exception as e:
            return [-1, -1, -1]

    def isEnabled(self, idx):
        return "enabled" in self.getStatus(idx)

    def setEnabled(self, idx, enable=True):
        try:
            self._getStage(idx).setEnabled(enable)
            return self.isEnabled(idx)
        except Exception as e:
            return False

    def toggleEnabled(self, idx):
        return self.setEnabled(idx, not self.isEnabled(idx))

    def getPosition(self, idx):
        try:
            return self._getStage(idx).getPosition()
        except Exception as e:
            return -1

    def isMoving(self, idx):
        try:
            return self._getStage(idx).isMoving()
        except Exception as e:
            return False

    def jog(self, idx, direction):
        try:
            self._getStage(idx).jog(direction)
        except Exception as e:
            return

    def startDrive(self, idx, direction):
        try:
            self._getStage(idx).startDrive(direction)
        except Exception as e:
            return

    def stopDrive(self, idx):
        try:
            self._getStage(idx).stopDrive()
        except Exception as e:
            return

    def move(self, idx, position):
        try:
            self._getStage(idx).move(position)
        except Exception as e:
            return

    def stopMove(self, idx):
        try:
            self._getStage(idx).stopMove()
        except Exception as e:
            return

    def home(self, idx, moveTo=False):
        try:
            self._getStage(idx).home(moveTo=moveTo)
        except Exception as e:
            return
