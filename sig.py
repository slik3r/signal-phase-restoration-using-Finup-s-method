
import math



class Signal:

    def create_gauss(self, N, fd, A, n, q, count=1):
        sig_arr = []
        for i in range(0, N):
            r = 0
            for k in range(count):
                r += A[k]*math.exp(-((i/fd-n[k])/q[k])**2)
            sig_arr.append(r)
        return sig_arr
