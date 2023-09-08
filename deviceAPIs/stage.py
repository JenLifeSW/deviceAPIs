from PySide6.QtCore import QThread, QTimer, Signal, Slot
from pylablib.devices import Thorlabs


TAG = "stage"


def use_mm(value):
    return value/1000


def use_um(value):
    return value/1000000


class Status:
    DISABLED = -1
    DEFAULT = 0
    IDLE = 1
    JOGGING = 2
    MOVING_NORMAL = 3
    MOVING_TO_ZERO = 4
    MOVING_TO_HOME = 5

    @classmethod
    def get_name(cls, code):
        status_dict = {
            cls.DISABLED: "DISABLED",
            cls.DEFAULT: "DEFAULT",
            cls.IDLE: "IDLE",
            cls.JOGGING: "JOGGING",
            cls.MOVING_NORMAL: "MOVING_NORMAL",
            cls.MOVING_TO_ZERO: "MOVING_TO_ZERO",
            cls.MOVING_TO_HOME: "MOVING_TO_HOME",
        }
        return status_dict.get(code, "UNKNOWN")


class Stage(QThread):
    numberOfStages = 1
    stage = []
    limit = [(0, use_mm(50)), (0, use_mm(50)), (0, use_mm(50))]
    driveDir = ["+", "+", "+"]
    status = [Status.DISABLED for _ in range(3)]
    homePosition = [0.0, 0.0, 0.0]

    connectedSignal = Signal(list)
    homedSignal = Signal()
    stoppingSignal = Signal(int)
    stoppedSignal = Signal(int, float)

    stageMovedSignal = Signal(int, float)
    errCannotDetect = Signal(str)
    errPositionLimit = Signal(str)
    normalLogSignal = Signal(str)

    driveTimer0 = QTimer()
    driveTimer1 = QTimer()
    driveTimer2 = QTimer()
    moveTimer0 = QTimer()
    moveTimer1 = QTimer()
    moveTimer2 = QTimer()
    timerInterval = 100

    def __init__(self, numberOfStages=1):
        super().__init__()
        self.initDevices(numberOfStages)

    def initDevices(self, numberOfStages):
        devices = []
        try:
            devices = Thorlabs.kinesis.list_kinesis_devices()
            if numberOfStages > len(devices):
                raise CanNotDetectSomeDevicesException()

            for idx, device in enumerate(devices):
                self.stage.append(Thorlabs.KinesisMotor(device[0], "MTS50-Z8"))
                self.stage[idx].setup_velocity(max_velocity=use_mm(5))
                self.stage[idx].setup_jog(step_size=use_mm(1))
                self.status[idx] = Status.DEFAULT
                # self.stageConnected[idx] = True

            self.numberOfStages = numberOfStages
            self.initTimer()
            self.stageMovedSignal.connect(self.onStageMoved)

        except CanNotDetectSomeDevicesException as e:
            print(f"$use: ${numberOfStages}, detected: ${len(devices)}, {e}")
        except Exception as e:
            print("\nKinesisMotor에 연결할 수 없습니다.", e)

        finally:
            self.checkConnected()

    def initTimer(self):
        self.driveTimer0.timeout.connect(self.jogToDrive0)
        self.driveTimer1.timeout.connect(self.jogToDrive1)
        self.driveTimer2.timeout.connect(self.jogToDrive2)

        self.moveTimer0.timeout.connect(self.checkMoving0)
        self.moveTimer1.timeout.connect(self.checkMoving1)
        self.moveTimer2.timeout.connect(self.checkMoving2)

    def close(self):
        for stage in self.stage:
            stage.close()

    def checkConnected(self):
            stageConnected = [self.status[idx] != Status.DISABLED for idx in range(3)]
            self.connectedSignal.emit(stageConnected)

    def setTimerInterval(self, interval):
        self.timerInterval = interval

    def setLimit(self, idx, bottom=use_mm(0), top=use_mm(50)):
        METHOD = "setLimit"
        print(f"{TAG}#{idx} {METHOD} {bottom}, {top}")
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD} 스테이지를 찾을 수 없습니다.")
            return

        self.limit[idx] = (bottom, top)

    def setUpVelocity(self, idx, maxVelocity, acc):
        self.stage[idx].setup_velocity(max_velocity=maxVelocity, acceleration=acc)

    def setUpJog(self, idx, size):
        self.stage[idx].setup_jog(step_size=size)

    def setEnabled(self, idx, enable=True):
        self.stage[idx]._enable_channel(enable)

    def isEnabled(self, idx):
        return "enabled" in self.stage[idx].get_status()

    def isMoving(self, idx):
        status = self.stage[idx].get_status()
        if (
                "moving_fw" not in status and
                "moving_bk" not in status and
                "jogging_fw" not in status and
                "jogging_bk" not in status
        ):
            return False
        else:
            return True

    def getPosition(self, idx):
        return self.stage[idx].get_position() - self.homePosition[idx]

    def home(self, idx):
        print(f"{idx} home")
        self.status[idx] = Status.MOVING_TO_ZERO
        self.move(idx, 0)

    @Slot(int)
    def onStageMoved(self, idx):
        print(f"[{idx}]onStageMoved {Status.get_name(self.status[idx])}")
        if self.status[idx] == Status.MOVING_TO_ZERO:
            self.status[idx] = Status.MOVING_TO_HOME
            self.jog(idx, "+")
            self.checkMoving(idx)
            return

        if self.status[idx] == Status.MOVING_TO_HOME:
            self.status[idx] = Status.IDLE
            self.homePosition[idx] = self.stage[idx].get_position()
            print(f"homePosition: {self.homePosition[idx]}")
            self.homedSignal.emit()

    def jog(self, idx, direction):
        '''
        direction: "+", "-"
        '''
        METHOD = "jog"
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD} 스테이지를 찾을 수 없습니다.")
            return

        if direction == "+":
            if (self.limit[idx][1] <= self.getPosition(idx)
                    and not (self.status[idx] == Status.MOVING_TO_ZERO
                             or self.status[idx] == Status.MOVING_TO_HOME)):
                print(f"{TAG}#{idx} {METHOD} 스테이지 상단 한계점 도달")
                self.errPositionLimit.emit(f"{TAG}#{idx} {METHOD} 스테이지 상단 한계점 도달")
                return
            self.stage[idx].jog("+", kind="builtin")
        elif direction == "-":
            if (self.getPosition(idx) <= self.limit[idx][0]
                    and not (self.status[idx] == Status.MOVING_TO_ZERO
                             or self.status[idx] == Status.MOVING_TO_HOME)):
                print(f"{TAG}#{idx} {METHOD} 스테이지 하단 한계점 도달")
                self.errPositionLimit.emit(f"{TAG}#{idx} {METHOD} 스테이지 하단 한계점 도달")
                return
            self.stage[idx].jog("-", kind="builtin")

    def jogToDrive0(self): self.jog(0, self.driveDir[0])
    def jogToDrive1(self): self.jog(1, self.driveDir[1])
    def jogToDrive2(self): self.jog(2, self.driveDir[2])

    def driveStart(self, idx, direction, isInitializing=False):
        TAG = "[driveStart]"
        print(f"{TAG} ${idx}, {direction}")
        '''
        direction: "+", "-"
        '''
        METHOD = "driveStart"
        '''
        limit 구현
        '''
        moveAble = True
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD} 스테이지를 찾을 수 없습니다.")
            return

        if direction == "+":
            if self.limit[idx][1] <= self.getPosition(idx) and self.status[idx] != Status.MOVING_TO_ZERO:
                print(f"{TAG}#{idx} {METHOD} 스테이지 상단 한계점 도달")
                self.errPositionLimit.emit(f"{TAG}#{idx} {METHOD} 스테이지 상단 한계점 도달")
                moveAble = False
        elif direction == "-":
            if self.getPosition(idx) <= self.limit[idx][0] and self.status[idx] != Status.MOVING_TO_ZERO:
                print(f"{TAG}#{idx} {METHOD} 스테이지 하단 한계점 도달")
                self.errPositionLimit.emit(f"{TAG}#{idx} {METHOD} 스테이지 하단 한계점 도달")
                moveAble = False

        self.driveDir[idx] = direction
        if moveAble:
            if idx == 0:
                self.driveTimer0.start(self.timerInterval)
            elif idx == 1:
                self.driveTimer1.start(self.timerInterval)
            else:
                self.driveTimer2.start(self.timerInterval)
        else:
            if idx == 0:
                self.driveTimer0.stop()
            elif idx == 1:
                self.driveTimer1.stop()
            else:
                self.driveTimer2.stop()

    def driveStop(self, idx):
        METHOD = "[driveStop]"
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD} 스테이지를 찾을 수 없습니다.")
            return

        if idx == 0:
            self.driveTimer0.stop()
        elif idx == 1:
            self.driveTimer1.stop()
        else:
            self.driveTimer2.stop()

    def move(self, idx, position):
        TAG = "[move]"
        print(f"{TAG}#{idx} {position}, {Status.get_name(self.status[idx])}")
        METHOD = "[move]"
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD}스테이지를 찾을 수 없습니다.")
            return

        if self.status[idx] == Status.MOVING_TO_ZERO:
            self.driveStart(idx, "-")

        if self.limit[idx][1] < position or position < self.limit[idx][0]:
            self.errPositionLimit.emit(f"{TAG}#{idx} {METHOD} 스테이지 한계점 이동불가 target:{position}, bot:{self.limit[idx][0]}, top:{self.limit[idx][1]}")
            return

        self.stage[idx].move_to(position)
        if idx == 0:
            self.moveTimer0.start(self.timerInterval)
        elif idx == 1:
            self.moveTimer1.start(self.timerInterval)
        else:
            self.moveTimer2.start(self.timerInterval)

    def checkMoving0(self): self.checkMoving(0)
    def checkMoving1(self): self.checkMoving(1)
    def checkMoving2(self): self.checkMoving(2)

    def checkMoving(self, idx, printLog=False, forStop=False):
        METHOD = "[checkMoving]"
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD}스테이지를 찾을 수 없습니다.")
            return

        status = self.stage[idx].get_status()
        print(f"{TAG}#{idx} {METHOD} status: {status}")
        if (
                "moving_fw" not in status and
                "moving_bk" not in status and
                "jogging_fw" not in status and
                "jogging_bk" not in status
        ):
            if idx == 0:
                self.moveTimer0.stop()
                self.driveTimer0.stop()
            elif idx == 1:
                self.moveTimer1.stop()
                self.driveTimer1.stop()
            else:
                self.moveTimer2.stop()
                self.driveTimer2.stop()

            if forStop:
                self.stoppedSignal.emit(idx, self.getPosition(idx))
            else:
                self.stageMovedSignal.emit(idx, self.getPosition(idx))

    def stopMove(self, idx, printLog=False):
        METHOD = "[stopMove]"
        if self.numberOfStages < idx:
            self.errCannotDetect.emit(f"{TAG}#{idx} {METHOD}스테이지를 찾을 수 없습니다.")
            return

        self.stoppingSignal.emit(idx)

        self.checkMoving(idx, printLog, True)
        self.stage[idx].stop(immediate=False)


class CanNotDetectSomeDevicesException(Exception):
    def __init__(self):
        super().__init__("모든 스테이지가 정상적으로 연결되었는지 확인하세요.")