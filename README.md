# JenLife SW용 API

## 레이저 제어 API

#### Signals
    - connectedSignal(bool)
        객체를 생성할 때 레이저 모듈이 연결되었는지 여부를 방출한다
    - currentSignal(float)
        레이저의 현재 소모 전력을 방출한다

---

#### Slots

    - turnOn()
        레이저의 전원을 켠다
    - turnOff()
        레이저의 전원을 끈다

## 스펙트로미터 제어 API

#### Signals

    - connectedSignal(bool)
        객체를 생성할 때 스펙트로미터 모듈이 연결되었는지 여부를 방출한다
    - infoSignal( (list<float>, list<float>) )
        스펙트럼의 wavelength와 indensity를 방출한다
    - ramanSignal( list<float> )
        스펙트럼을 ramanShift한 결과를 방출한다

---

#### Slots

    - getRamanShift(float)
        스펙트럼을 ramanShift한 결과를 요청한다

## 스테이지 제어 API

#### Signals

    - allStageConnected(bool)
        객체를 생성할 때 모든 스테이지가 연결되었는지 여부를 방출한다
    - stagePositionSignals[idx](float)
        idx번 스테이지의 현재 위치를 방출한다
    - stageMovedSignals[idx]()
        idx번 스테이지의 move 과정이 완료되었을 때 방출한다

---

#### Slots

    - setStepSize(idx, size)
        idx번 스테이지의 스텝사이즈를 size로 조정한다
    - getPosition(idx)
        idx번 스테이지의 현재 위치를 요청한다
    - jog(idx, direction)
        idx번 스테이지를 direction 방향으로 조그한다
    - drive(idx, direction)
        idx번 스테이지를 direction 방향으로 drive한다
    - driveStop(idx)
        idx번 스테이지의 drive를 멈춘다
    - move(idx, position)
        idx번 스테이지를 position 위치로 이동한다

## 스테이지 v2

#### Signals
    [idx는 스테이지의 인덱스를 나타냄]
    - errorCanNotConnectToDevice: Signal(idx: int)
        스테이지에 연결하지 못했을 때 발생
    - errorPositionLimit: Signal(idx: int, msg: str)
        스테이지를 이동할 수 없음.
    - connectedSignal: Signal(idx: int, result: bool)
        스테이지가 연결되거나 연결이 끊겼을 때 발생
    - homedSignal: Signal(idx: int)
        스테이지가 homed되었음
    - stoppingSignal: Signal(idx: int)
        스테이지에 stop 명령이 전달되었음
    - stoppedSignal: Signal(idx: int, position: float)
        스테이지 stop 명령 후 멈췄을 때 현재 위치를 방출
    - movedSiganl: Signal(idx: int, position: float)
        스테이지가 이동완료됐을 때 현재 위치를 방출

#### Method
    - close()
        프로그램 종료 전, 스테이지의 연결을 끊기위해 호출
    - getTimerInterval(idx: int): int
        drive 사용시 jog 명령을 수행하는 주기(ms)
    - setTimerInterval(idx: int, interval: int)
        drive 사용시 jog 명령을 수행할 주기 수정(ms)
    - getCondition(idx: int): int
        stageUnit의 현재 상태(DISABLED, IDLE 등 stageControlUnit.Condition 참고)
    - getStatus(idx: int): list<str>
        키네시스 라이브러리가 제공하는 스테이지의 상태
    - isHomed(idx: int): bool
        homed 여부
    - setLimit(idx: int, bottom: float, top: float):
        스테이지의 이동 한계 수동 설정
    - getJogParameters(idx: int): list
        TJogParams(mode, step_size, min_velocity, acceleration, max_velocity, stop_mode='profiled')
    - getVelocityParameters(idx: int): list
        TVelocityParams(min_velocity, acceleration, max_velocity)
    - setupJog(idx: int, size:float, minVelocity: float, maxVelocity: float, acceleration: float): TJogParams
        jog 설정
    - setupVelocity(idx: int, minVelocity: float, maxVelocity: float, acceleration: float): TVelocityParams
        velocity 설정
    - isEnabled(idx: int): bool
        스테이지 활성화 여부
    - setEnabled(idx: int, enable: bool): bool
        스테이지 활성화 상태 변경
    - toggleEnabled(idx: int): bool
        스테이지 활성화 토글
    - getPosition(idx: int): float
        현재 위치 조회
    - isMoving(idx: int): bool
        현재 이동중인지 여부
    - jog(idx: int, direction: str)
        direction 방향으로 1step 이동 ("+" or "-")
    - startDrive(idx: int, direction: str)
        direction 방향으로 이동 시작
    - stopDrive(idx: int)
        drive 중지
    - move(idx: int, postion: float)
        position으로 이동
    - stopMove(idx: int)
        이동 중지
    - home(idx: int)
        home 설정
