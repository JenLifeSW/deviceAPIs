import seatease.spectrometers as st
import seabreeze.spectrometers as sb


class Spectrometer():
    def __init__(self, isVirtual=False):
        super().__init__()
        self.spec = st.Spectrometer.from_first_available() if isVirtual else sb.Spectrometer.from_first_available()
        self.setIntegrationTime(100000)

    def setIntegrationTime(self, value):
        self.spec.integration_time_micros(value)

    def getSpectrum(self):
        return self.spec.spectrum()

    def getWavelength(self):
        return self.getSpectrum()[0]

    def getIntensities(self):
        return self.getSpectrum()[1]
