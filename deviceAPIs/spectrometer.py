import seatease.spectrometers as st
import seabreeze.spectrometers as sb
from PySide6.QtCore import QThread


class Spectrometer(QThread):
    def __init__(self, virtual=False):
        self.spec = st.Spectrometer.from_first_available() if virtual else sb.Spectrometer.from_first_available()
        self.setIntegrationTime(100000)

    def setIntegrationTime(self, value):
        self.spec.integration_time_micros(value)

    def getSpectrum(self):
        return self.spec.spectrum()

    def getWavelength(self):
        return self.getSpectrum()[0]

    def getIntensities(self):
        return self.getSpectrum()[1]
