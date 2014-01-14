# this tiny python script will create a webcam window for multiple USB devices
# 
# Currently, calling the program with the following prompt:
#
#   $ python ./webcam.py 1 3
#
# will create a webcam window for USB devices 1 and 3. In the future, this behavior 
# should be modified so that a seperate 'USBWidget' window opens, displaying a 
# list of connected USB devices and allowing the user to create 'VideoWidget'
# instances for as many USB devices as desired.
#
# dependencies: 
#   - PyQt4 (algthough PySide should also work)
#   - PIL
#   - cv (PyOpenCV)
#
# created by jonbrennecke / http://jonbrennecke.com/
#
#

import cv, sys
from PIL import Image, ImageQt
from PyQt4 import QtGui, QtCore

class USBWidget(QtGui.QWidget) :
    def __init__(self) :
        super(USBWidget, self).__init__()

# main VideoWidget window
class VideoWidget(QtGui.QWidget) :
    def __init__(self,idx) :
        super(VideoWidget, self).__init__()
        self.idx = idx;
        self.capture = cv.CreateCameraCapture(idx)
        frame = cv.QueryFrame(self.capture)
        self.size = (frame.width,frame.height)
        self.pixmap = QtGui.QPixmap(frame.width,frame.height)
        self.painter = QtGui.QPainter(self.pixmap)
        self.initUI()

        self._frame = None
        self.image = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.queryFrame)
        self.timer.start(50)

    def initUI(self):
        self.setGeometry(300,300,self.size[0],self.size[1])
        self.setWindowTitle('Super Mouse Cam '+str(self.idx))

        # label
        self.lbl = QtGui.QLabel(self)
        self.lbl.move(0,0)
        self.lbl.setGeometry(0,0,self.size[0],self.size[1])

        # horizontal box
        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)
        self.show()

    def mkImage(self,frame):
        try:
            if not self._frame:
                self._frame = cv.CreateImage((frame.width, frame.height), cv.IPL_DEPTH_8U, frame.nChannels)
            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Copy(frame, self._frame)
            else:
                cv.Flip(frame, self._frame, 0)
            return IplQImage(self._frame)
        except AttributeError:
            pass 

    def queryFrame(self):
        frame = cv.QueryFrame(self.capture)
        self.image = self.mkImage(frame)
        self.update()

    def paintEvent(self, event):
        if self.image :
            self.painter.drawImage(QtCore.QPoint(0, 0), self.image)
            self.lbl.setPixmap(self.pixmap)

# A class for converting iplimages to qimages
# based on http://matthewshotton.wordpress.com/2011/03/31/python-opencv-iplimage-to-pyqt-qimage/
class IplQImage(QtGui.QImage):
    def __init__(self,iplimage):
        # Rough-n-ready but it works dammit
        alpha = cv.CreateMat(iplimage.height,iplimage.width, cv.CV_8UC1)
        cv.Rectangle(alpha, (0, 0), (iplimage.width,iplimage.height), cv.ScalarAll(255) ,-1)
        rgba = cv.CreateMat(iplimage.height, iplimage.width, cv.CV_8UC4)
        cv.Set(rgba, (1, 2, 3, 4))
        cv.MixChannels([iplimage, alpha],[rgba], [
        (0, 0), # rgba[0] -> bgr[2]
        (1, 1), # rgba[1] -> bgr[1]
        (2, 2), # rgba[2] -> bgr[0]
        (3, 3)  # rgba[3] -> alpha[0]
        ])
        self.__imagedata = rgba.tostring()
        super(IplQImage,self).__init__(self.__imagedata, iplimage.width, iplimage.height, QtGui.QImage.Format_RGB32)
 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = VideoWidget(1)

    app2 = QtGui.QApplication(sys.argv)
    ex2 = VideoWidget(2)

    sys.exit(app.exec_())
