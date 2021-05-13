import numpy as np
import time
import cv2
import pylab
from imutils import face_utils
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class findFaceGetPulse(object):

    def __init__(self, bpm_limits=[], data_spike_limit=250,
                 face_detector_smoothness=10):

        self.frame_in = np.zeros((10, 10))
        self.frame_out = np.zeros((10, 10))
        self.fps = 0
        self.buffer_size = 250
        #self.window = np.hamming(self.buffer_size)
        self.data_buffer = []
        self.times = []
        self.ttimes = []
        self.samples = []
        self.freqs = []
        self.fft = []
        self.slices = [[0]]
        self.t0 = time.time()
        self.bpms = []
        self.bpm = 0
        self.forehead=[]
        dpath = resource_path("haarcascade_frontalface_alt.xml")
        if not os.path.exists(dpath):
            print("Cascade file not present!")
        self.face_cascade = cv2.CascadeClassifier(dpath)
        self.face_rect = [1, 1, 2, 2]
        self.last_center = np.array([0, 0])
        self.last_wh = np.array([0, 0])
        self.output_dim = 13
        self.trained = False

        self.idx = 1
        self.find_faces = True

    def find_faces_toggle(self):
        self.find_faces = not self.find_faces
        return self.find_faces

    def get_faces(self):
        return

    def shift(self, detected):
        x, y, w, h = detected
        center = np.array([x + 0.5 * w, y + 0.5 * h])
        shift = np.linalg.norm(center - self.last_center)

        self.last_center = center
        return shift

    def get_leftCheekRect(self):
        x, y, w, h = self.face_rect
        return [x+40, int(y+h/2), int(w/5), int(h/5)]

    def get_rightCheekRect(self):
        x, y, w, h = self.face_rect
        return [x+240, int(y+h/2), int(w/5), int(h/5)]

    def draw_rect(self, rect, col=(0, 255, 0)):
        x, y, w, h = rect
        cv2.rectangle(self.frame_out, (x, y), (x + w, y + h), col, 1)

    def displayColorInfo(self, info, pos, text):
        textR="Avarage Color H of %s : %d" % (text, info[0])
        textG="Avarage Color S of %s : %d" % (text, info[1])
        textB="Avarage Color V of %s : %d" % (text, info[2])
        cv2.putText(self.frame_out, textR,
                    (10, pos[0]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))
        cv2.putText(self.frame_out, textG,
                    (10, pos[1]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))
        cv2.putText(self.frame_out, textB,
                    (10, pos[2]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255))

    def get_subface_coord(self, fh_x, fh_y, fh_w, fh_h):
        x, y, w, h = self.face_rect
        return [int(x + w * fh_x - (w * fh_w / 2.0)),
                int(y + h * fh_y - (h * fh_h / 2.0)),
                int(w * fh_w),
                int(h * fh_h)]

    def get_subface_means(self, coord):
        x, y, w, h = coord
        subframe = self.frame_in[y:y + h, x:x + w, :]
        subframeHSV = cv2.cvtColor(subframe, cv2.COLOR_BGR2HSV)
        v1 = int(np.mean(subframeHSV[:, :, 0]))
        v2 = int(np.mean(subframeHSV[:, :, 1]))
        v3 = int(np.mean(subframeHSV[:, :, 2]))
        return [v1, v2, v3]

    def get_foreheadRect(self):
        return self.forehead

    def train(self):
        self.trained = not self.trained
        return self.trained

    def plot(self):
        data = np.array(self.data_buffer).T
        np.savetxt("data.dat", data)
        np.savetxt("times.dat", self.times)
        freqs = 60. * self.freqs
        idx = np.where((freqs > 50) & (freqs < 180))
        pylab.figure()
        n = data.shape[0]
        for k in xrange(n):
            pylab.subplot(n, 1, k + 1)
            pylab.plot(self.times, data[k])
        pylab.savefig("data.png")
        pylab.figure()
        for k in xrange(self.output_dim):
            pylab.subplot(self.output_dim, 1, k + 1)
            pylab.plot(self.times, self.pcadata[k])
        pylab.savefig("data_pca.png")

        pylab.figure()
        for k in xrange(self.output_dim):
            pylab.subplot(self.output_dim, 1, k + 1)
            pylab.plot(freqs[idx], self.fft[k][idx])
        pylab.savefig("data_fft.png")
        quit()
 
    def run(self, cam):
        self.times.append(time.time() - self.t0)
        self.frame_out = self.frame_in
        self.gray = cv2.equalizeHist(cv2.cvtColor(self.frame_in, cv2.COLOR_BGR2GRAY))
        col = (100, 255, 100)
        if self.find_faces:
            self.data_buffer, self.times, self.trained = [], [], False
            detected = list(self.face_cascade.detectMultiScale(self.gray, scaleFactor=1.3,
                                                               minNeighbors=4, minSize=(50, 50),
                                                               flags=cv2.CASCADE_SCALE_IMAGE))

            if len(detected) > 0:
                detected.sort(key=lambda a: a[-1] * a[-2])

                if self.shift(detected[-1]) > 10:
                    self.face_rect = detected[-1]
            forehead1 = self.get_subface_coord(0.5, 0.18, 0.25, 0.15)
            self.forehead=forehead1
            self.draw_rect(self.face_rect, col=(255, 0, 0))
            
            x, y, w, h = self.face_rect
            cv2.putText(self.frame_out, "Face",
                       (x, y), cv2.FONT_HERSHEY_PLAIN, 1.2, col)
           
        if set(self.face_rect) == set([1, 1, 2, 2]): return
        
