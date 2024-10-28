import math
import random
import cmath
import time

from scipy.fft import ifft, fft


class Fienup:

    def __init__(self, tau, s, data, input_arr):
        self.cmplx1 = []
        self.cmplx2 = []
        self.s1 = 1
        self.s2 = 0
        self.x = input_arr
        self.N = len(s)
        self.S = []
        for i in range(self.N):
            self.S.append(math.sqrt(s[i].imag**2+s[i].real**2))
        self.tau = tau
        self.data = data

    def start(self):
        self.cmplx1 = []
        self.cmplx2 = []
        for i in range(self.N):
            phi = random.uniform(0, 1) * 2 * math.pi
            self.cmplx2.append(complex(self.S[i]*math.cos(phi), self.S[i]*math.sin(phi))) # преобразование во временную

        calc = 0
        while abs(self.s1-self.s2) > self.tau:
            self.s1 = self.s2
            self.cmplx1 = self.cmplx2

            self.cmplx2 = list(ifft(self.cmplx2))
            self.cmplx1 = list(ifft(self.cmplx1))

            self.data.xr = []
            for i in range(self.N):
                self.data.xr.append(self.cmplx2[i].real)

            for i in range(self.N):
                real = self.cmplx2[i].real
                if real < 0:
                    real = 0
                self.cmplx2[i] = complex(real, 0)

            self.cmplx2 = list(fft(self.cmplx2))
            for j in range(self.N):

                phase = math.atan2(self.cmplx2[j].imag, self.cmplx2[j].real)
                self.cmplx2[j] = complex(self.S[j]*math.cos(phase), self.S[j]*math.sin(phase))

            self.cmplx2 = list(ifft(self.cmplx2))
            self.s2 = 0

            for i in range(self.N):
                self.s2 += math.sqrt((self.cmplx1[i].real-self.cmplx2[i].real)**2)
            self.cmplx2 = list(fft(self.cmplx2))
#calc += 1
        self.cmplx2 = list(ifft(self.cmplx2))
        self.xr = []
        for i in range(self.N):
            self.xr.append(self.cmplx2[i].real)
        return self.xr


   #Сдвиг на 1
    def shift(self):
        buf = self.xr[:]
        for i in range(self.N-1):
            self.xr[i+1] = buf[i]
        self.xr[0] = buf[self.N-1]

   #Отражение
    def reflection(self):
        buf = self.xr[:]
        for i in range(self.N):
            self.xr[i] = buf[self.N-1-i]

    def get_error(self):
        buf = []
        for i in range(self.N):
            buf.append(abs(self.x[i]-self.xr[i]))# массив x наш входной сигнал, xr наш востановленный сигнал

        return max(buf)

    # def correct(self):
    #     for i in range(self.N):
    #         self.shift()
    #         if self.get_error() <= 0.2 * max(self.x):
    #             self.is_solve = True
    #             break
    #         if i == (self.N-1) and self.get_error() >= 0.2 * max(self.x):
    #             self.reflection()

    def correct(self):

        min_i = 0
        min_v = 999
        is_reflection = False
        for i in range(self.N):
            error = self.get_error()
            if min_v > error:
                min_v = error
                min_i = i

            self.shift()
        self.reflection()
        for i in range(self.N):
            error = self.get_error()
            if min_v > error:
                min_v = error
                min_i = i
                is_reflection = True

            self.shift()
        if not is_reflection:
            self.reflection()
        for i in range(min_i):
            self.shift()

