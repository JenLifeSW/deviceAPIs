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
