# This is a basic version of Audio Spectrum Analyzer based on PyQtGraph
# Just basic FFT and spectrum auto scaling

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyaudio
from scipy.fftpack import fft


class SpectrumAnalyzer:
    def __init__(self):

        # set audio options
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # mono for mics
        self.RATE = 44100
        self.CHUNK = 2048  # adjustable
        # set audio stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            frames_per_buffer=self.CHUNK,
            # stream_callback=callback,
            input=True,
            output=True,
        )

        # set window size
        self.desktop = QtGui.QApplication.desktop()
        self.screen = self.desktop.screenGeometry()
        self.height = self.screen.height()
        self.width = self.screen.width()
        # set window position
        self.window = pg.GraphicsWindow()
        self.window.setGeometry(self.width/4, self.height/4, self.width/2, self.height/2)
        self.window.setWindowTitle('Audio Spectrum Analyzer')

        self.waveform = self.window.addPlot(title='Waveform', row=0, col=0)
        self.spectrum = self.window.addPlot(title='Spectrum', row=1, col=0)

        # scaling
        self.waveform.setYRange(-1, 1, padding=0)
        self.spectrum_max = 2048  # initial upper limit
        self.spectrum.setYRange(0, self.spectrum_max, padding=0)

        # set x indexes
        self.t = np.arange(0, self.CHUNK)  # samples indexes
        self.f = np.linspace(0, self.RATE/2, int(self.CHUNK/2))  # frequency indexes

        # set curves
        self.waveform_plot = self.waveform.plot(pen='g')
        self.spectrum_plot = self.spectrum.plot(pen='r')

    def update(self):
        # fetch data from stream
        data = self.stream.read(self.CHUNK)  # original binary data
        waveform_data = np.frombuffer(data, dtype=np.int16).astype(float)
        # update curve
        self.waveform_plot.setData(self.t, waveform_data / 2**16)  # normalization

        # run Fast Fourier Transform
        spectrum_data = fft(np.array(waveform_data, dtype=np.int16))
        spectrum_data = np.abs(spectrum_data[0:int(self.CHUNK / 2)]) * 2 / self.CHUNK
        # update y range
        if max(spectrum_data) > self.spectrum_max:
            self.spectrum_max = max(spectrum_data)
        self.spectrum.setYRange(0, self.spectrum_max, padding=0)
        # update curve
        self.spectrum_plot.setData(self.f, spectrum_data)


# set PyQtGraph global configuration options
pg.setConfigOptions(leftButtonPan=True, foreground='w', antialias=False)
# enabling anti-aliasing causes lines to be drawn with smooth edges at the cost of reduced performance

# set QtGui instance
app = QtGui.QApplication([])

# start core program
sa = SpectrumAnalyzer()

# set and start timer
timer = QtCore.QTimer()
timer.timeout.connect(sa.update)
timer.start(0)

# start Qt event loop unless running in interactive mode or using pyside
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
