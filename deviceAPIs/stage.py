from PySide6.QtCore import QThread, QTimer, Signal
from pylablib.devices import Thorlabs


class Stage(QThread):
    stages = []
    allStageConnected = Signal(bool)

    def __init__(self, numberOfStages=1):
        super().__init__()
        devices = []
        try:
            devices = Thorlabs.kinesis.list_kinesis_devices()
            if numberOfStages > len(devices):
                raise CanNotDetectSomeDevicesException()

            for idx, device in enumerate(devices):
                self.stages.append(Thorlabs.KinesisMotor(device[0], "MTS50-Z8"))
                self.stages[idx].setup_velocity(min_velocity=0.0001, max_velocity=0.001)

            self.allStageConnected.emit(True)

        except CanNotDetectSomeDevicesException as e:
            print(f"$use: ${numberOfStages}, detected: ${len(devices)}, {e}")
            self.allStageConnected.emit(False)
        except Exception as e:
            print("\nKinesisMotor에 연결할 수 없습니다.", e)
            self.allStageConnected.emit(False)

        self.stepSize = [0.01 for _ in range(numberOfStages)]
        self.driveDirs = ["+" for _ in range(numberOfStages)]
        self.driveTimers = [QTimer() for _ in range(numberOfStages)]
        for idx, timer in enumerate(self.driveTimers):
            timer.timeout.connect(lambda: self.jog(idx, self.driveDirs[idx]))
        self.moveToPositions = [0 for _ in range(numberOfStages)]
        self.moveTimers = [QTimer() for _ in range(numberOfStages)]
        for idx, timer in enumerate(self.moveTimers):
            timer.timeout.connect(lambda: self.moveCheck(idx))
        self.stageMovedSignals = [Signal() for _ in range(numberOfStages)]

    def setStepSize(self, idx, size):
        self.stepSize[idx] = size

    def getPosition(self, idx):
        return self.stages[idx].get_position(True) * 1000

    def jog(self, idx, direction):
        self.stages[idx].setup_jog(step_size=self.stepSize[idx])
        self.stages[idx].jog(direction, kind="builtin")

    def driveStart(self, idx, direction):
        self.driveDirs[idx] = direction
        self.driveTimers[idx].start(100)

    def driveStop(self, idx):
        self.driveTimers[idx].stop()

    def moveTo(self, idx, position):
        self.stages[idx].move_to(position)
        self.moveTimers[idx].start(100)

    def moveCheck(self, idx):
        if self.stages[idx].get_status() == "enabled":
            self.moveTimers[idx].stop()
            self.stageMovedSignals[idx].emit()


class CanNotDetectSomeDevicesException(Exception):
    def __init__(self):
        super().__init__("모든 스테이지가 정상적으로 연결되었는지 확인하세요.")