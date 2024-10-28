import math
import random
import sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, QThread
import draw
import sig
from scipy.fft import *
import fienup


class Data:

    def __init__(self):
        self.xr = []
        self.stop = False


data = Data()


class Worker(QThread):
    def __init__(self, tau, spectrum_arr, input_arr, parent=None):
        self.tau = tau
        self.spectrum_arr = spectrum_arr
        self.input_arr = input_arr
        super(Worker, self).__init__(parent)

    def run(self):
        fie = fienup.Fienup(self.tau, self.spectrum_arr, data, self.input_arr)
        data.xr = fie.start()
        fie.correct()
        data.stop = True


class App(QMainWindow):

    def __init__(self, template_filename):
        super(App, self).__init__()
        self.app = QtWidgets.QApplication([])
        self.root = uic.loadUi(template_filename)

        self.signal = sig.Signal()

        self.root.executeBtn.clicked.connect(self.execute)

        self.x = [0, 1]
        self.y = [0, 0]
        self.y2 = [0, 0]

        self.sg = draw.Draw(self.root, self.root.signal_graph, title="Исходный и восстановленный сигналы", label_horizontal="t", label_vertical="A")
        self.sg.pen([(255, 0, 0), (0, 0, 255)], [2, 2])
        self.sg.create_data(self.x, [self.y, self.y2])

        self.spg = draw.Draw(self.root, self.root.spectrum_graph, title="Спектр исходного сигнала", label_horizontal="f", label_vertical="A")
        self.spg.pen([(255, 0, 0), (0, 0, 255)], [2, 2])
        self.spg.create_data(self.x, self.y)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot_data)

        self.root.show()

    def energy_delta(self, x, y):
        return sum([(v1-v2)**2 for v1, v2 in zip(x, y)])

    def update_plot_data(self):
        if len(data.xr) > 0 and not data.stop:
            self.sg.update_data(self.t_arr, [self.input_arr, data.xr])
        elif data.stop:
            self.root.executeBtn.setEnabled(True)
            self.sg.update_data(self.t_arr, [self.input_arr, data.xr])
            self.root.edit_enery_delta.setText(str(round(self.energy_delta(self.input_arr, data.xr), 5)))
            data.stop = False
            self.timer.stop()

    def execute(self):
        self.root.executeBtn.setEnabled(False)
        self.x = [i for i in range(100)]

        self.y = [random.randint(0, 100) for _ in range(100)]

        self.N = int(self.root.edit_N.text())
        self.fd = float(self.root.edit_fd.text())
        self.A1 = float(self.root.edit_A1.text())
        self.n1 = float(self.root.edit_n1.text())
        self.q1 = float(self.root.edit_q1.text())
        self.A2 = float(self.root.edit_A2.text())
        self.n2 = float(self.root.edit_n2.text())
        self.q2 = float(self.root.edit_q2.text())
        self.A3 = float(self.root.edit_A3.text())
        self.n3 = float(self.root.edit_n3.text())
        self.q3 = float(self.root.edit_q3.text())

        self.tau = 1.e-6

        self.t_arr = [i/self.fd for i in range(self.N)]

        self.input_arr = self.signal.create_gauss(self.N, self.fd,
                                                  A=[self.A1, self.A2, self.A3],
                                                  q=[self.q1, self.q2, self.q3],
                                                  n=[self.n1, self.n2, self.n3], count=3)

        self.spectrum_arr = list(fft(self.input_arr))
        self.spectrum_arr_abs = []

        for val in self.spectrum_arr:
            self.spectrum_arr_abs.append(math.sqrt(val.imag**2+val.real**2))
        self.spg.update_data([self.fd*i/self.N for i in range(self.N)], self.spectrum_arr_abs)

        self.thread = Worker(self.tau, self.spectrum_arr, self.input_arr)
        self.thread.start()
        self.timer.start()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = App(template_filename="template.ui")
    sys.exit(app.exec_())
