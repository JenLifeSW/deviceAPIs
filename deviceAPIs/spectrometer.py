import seatease.spectrometers as st
import seabreeze.spectrometers as sb
from PySide6.QtCore import Signal


class Spectrometer():
    spectrometerConnected = Signal(bool)

    def __init__(self, isVirtual=False):
        super().__init__()
        try:
            self.spec = st.Spectrometer.from_first_available() if isVirtual else sb.Spectrometer.from_first_available()
            self.setIntegrationTime(100000)
            self.spectrometerConnected.emit(True)
        except Exception as e:
            print("스펙트로미터 장치에 연결할 수 없습니다.", e)
            self.spectrometerConnected.emit(False)

    def setIntegrationTime(self, value):
        self.spec.integration_time_micros(value)

    def getSpectrum(self):
        return self.spec.spectrum()

    def getWavelength(self):
        return self.getSpectrum()[0]

    def getIntensities(self):
        return self.getSpectrum()[1]

    def getRamanShift(self, laserWavelength):
        return (1 / laserWavelength - 1 / self.getWavelength()) * (10 ** 7)