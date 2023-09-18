from PySide6.QtCore import QTimer, Signal, Slot, QObject
from pylablib.devices import Thorlabs


TAG = "stageUnit"


def use_mm(value):
    return value/1000


def use_um(value):
    return value/1000000


class Condition:
    DISABLED = -1
    DEFAULT = 0
    IDLE = 1
    JOGGING = 2
    MOVING_NORMAL = 3
    MOVING_TO_GROUND = 4
    MOVING_TO_HOME = 5

    @classmethod
    def get_name(cls, code):
        status_dict = {
            cls.DISABLED: "DISABLED",
            cls.DEFAULT: "DEFAULT",
            cls.IDLE: "IDLE",
            cls.JOGGING: "JOGGING",
            cls.MOVING_NORMAL: "MOVING_NORMAL",
            cls.MOVING_TO_GROUND: "MOVING_TO_GROUND",
            cls.MOVING_TO_HOME: "MOVING_TO_HOME",
        }
        return status_dict.get(code, "UNKNOWN")


class StageControlUnit(QObject):
    serial = -1
    stage = None
    limit = (0.0, use_mm(50.0))
    driveDir = "+"
    condition = Condition.DISABLED

    initedSignal = Signal()
    homedSignal = Signal()
    stoppingSignal = Signal()
    stoppedSignal = Signal(float)

    stageMovedSignal = Signal(float)
    errorPositionLimit = Signal(str)
    normalLogSignal = Signal(str)

    driveTimer = QTimer()
    checkMovingTimer = QTimer()
    timerInterval = 100
    waitToHomed = 2000

    def __init__(self, serial):
        super().__init__()
        self.initDevices(serial)

    def initDevices(self, serial):
        self.serial = serial

        self.stage = Thorlabs.KinesisMotor(serial, "MTS50-Z8")
        self.setupVelocity(maxVelocity=use_mm(1), acceleration=use_mm(1))
        self.setupJog(size=use_mm(1), maxVelocity=use_mm(1), acceleration=use_mm(1))
        self._setCondition(Condition.DEFAULT)

        self.initTimer()
        self.stageMovedSignal.connect(self.onStageMoved)
        self.errorPositionLimit.connect(self.onErrEmitted)

        QTimer().singleShot(100, lambda :self.initedSignal.emit())

    @Slot(str)
    def onErrEmitted(self, msg):
        print(msg)

    def initTimer(self):
        self.driveTimer.timeout.connect(lambda: self.jog(self.driveDir))
        self.checkMovingTimer.timeout.connect(self.checkMoving)

    def disconnectTimer(self):
        self.driveTimer.timeout.disconnect()
        self.checkMovingTimer.timeout.disconnect()

    def close(self):
        self.disconnectTimer()
        self.stage.close()

    def isConnected(self):
        self.stage.is_connected()

    def getTimerInterval(self):
        return self.timerInterval

    def setTimerInterval(self, interval):
        self.timerInterval = interval

    def getCondition(self):
        return self.condition

    def _setCondition(self, condition):
        self.condition = condition

    def getStatus(self):
        return self.stage.get_status()

    def isHomed(self):
        return "homed" in self.getStatus()

    def setLimit(self, bottom=use_mm(0), top=use_mm(50)):
        self.limit = (bottom, top)

    def getJogParameters(self):
        return self.stage._get_jog_parameters()

    def getVelocityParameters(self):
        return self.stage._get_velocity_parameters()

    def setupJog(self, size=None, minVelocity=None, maxVelocity=None, acceleration=None):
        return self.stage.setup_jog(step_size=size, min_velocity=minVelocity, max_velocity=maxVelocity, acceleration=acceleration)

    def setupVelocity(self, minVelocity=None, maxVelocity=None, acceleration=None):
        return self.stage.setup_velocity(min_velocity=minVelocity, max_velocity=maxVelocity, acceleration=acceleration)

    def isEnabled(self):
        return "enabled" in self.getStatus()

    def setEnabled(self, enable=True):
        self.stage._enable_channel(enable)

    def getPosition(self):
        return self.stage.get_position()

    def isMoving(self):
        status = self.getStatus()
        return (
                "moving_fw" in status or
                "moving_bk" in status or
                "jogging_fw" in status or
                "jogging_bk" in status
        )

    def jog(self, direction):
        '''
        direction: "+", "-"
        '''
        METHOD = "[jog]"

        if direction == "+":
            if (self.limit[1] <= self.getPosition()
                    and not (self.getCondition() == Condition.MOVING_TO_GROUND
                             or self.getCondition() == Condition.MOVING_TO_HOME)):
                self.errorPositionLimit.emit(f"{TAG}#{self.serial} {METHOD} 스테이지 상단 한계점 도달")
                return
            self.stage.jog("+", kind="builtin")
        elif direction == "-":
            if (self.getPosition() <= self.limit[0]
                    and not (self.getCondition() == Condition.MOVING_TO_GROUND
                             or self.getCondition() == Condition.MOVING_TO_HOME)):
                self.errorPositionLimit.emit(f"{TAG}#{self.serial} {METHOD} 스테이지 하단 한계점 도달")
                return
            self.stage.jog("-", kind="builtin")

    @Slot(str)
    def setDriveDir(self, driveDir):
        self.driveDir = driveDir

    def startDriveTimer(self):
        self.driveTimer.start(self.timerInterval)

    def stopDriveTimer(self):
        self.driveTimer.stop()

    def startCheckMovingTimer(self):
        self.checkMovingTimer.start(self.timerInterval)

    def stopCheckMovingTimer(self):
        self.checkMovingTimer.stop()

    def startDrive(self, direction):
        """
        direction: "+", "-"
        """

        moveAble = True
        self.driveDir = direction
        if direction == "+":
            if self.limit[1] <= self.getPosition() and self.getCondition() != Condition.MOVING_TO_GROUND:
                self.errorPositionLimit.emit(f"{TAG}#{self.serial} {METHOD} 스테이지 상단 한계점 도달")
                moveAble = False
        elif direction == "-":
            if self.getPosition() <= self.limit[0] and self.getCondition() != Condition.MOVING_TO_GROUND:
                self.errorPositionLimit.emit(f"{TAG}#{self.serial} {METHOD} 스테이지 하단 한계점 도달")
                moveAble = False

        self.setDriveDir(direction)
        if moveAble:
            self.startDriveTimer()
        else:
            self.stopDriveTimer()

    def stopDrive(self):
        self.stopDriveTimer()

    def checkMoving(self, forStop=False):
        if not self.isMoving():
            self.stopCheckMovingTimer()
            self.stopDriveTimer()

            if forStop:
                self.stoppedSignal.emit(self.getPosition())
            else:
                self.stageMovedSignal.emit(self.getPosition())

    def move(self, position):
        METHOD = "[move]"

        if self.limit[1] < position or position < self.limit[0]:
            self.errorPositionLimit.emit(f"{TAG}#{self.serial} {METHOD} 스테이지 한계점 이동불가 target:{position}, bot:{self.limit[0]}, top:{self.limit[1]}")
            return

        self.stage.move_to(position)
        self.startCheckMovingTimer()

    def stopMove(self):
        self.stoppingSignal.emit()
        self.checkMoving(True)
        self.stage.stop(immediate=False)

    def moveToGround(self):
        self.startDrive("-")
        QTimer.singleShot(self.timerInterval, self.startCheckMovingTimer)

    @Slot(int)
    def onStageMoved(self):
        if self.getCondition() == Condition.MOVING_TO_GROUND:
            self._setCondition(Condition.MOVING_TO_HOME)
            self.stage._home(sync=False, force=True)

            self.startCheckMovingTimer()

            return

        if self.getCondition() == Condition.MOVING_TO_HOME:
            QTimer.singleShot(self.waitToHomed, self.setHomed)

    def home(self, moveTo=False):
        if self.isHomed():
            if moveTo:
                self._setCondition(Condition.MOVING_TO_HOME)
                self.move(0)
                return
            else:
                self.homedSignal.emit()
                return

        self._setCondition(Condition.MOVING_TO_GROUND)
        self.moveToGround()

    @Slot(int)
    def setHomed(self):
        if not self.isMoving():
            print(f"{TAG}#{self.serial} homed")
            self._setCondition(Condition.IDLE)
            self.homedSignal.emit()
            return

        QTimer.singleShot(self.waitToHomed, self.setHomed)


class CanNotDetectDeviceException(Exception):
    def __init__(self):
        super().__init__("스테이지를 찾을 수 없습니다.")
