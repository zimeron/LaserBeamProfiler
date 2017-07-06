#!/usr/bin/env python
# Copyright (C) 2015 Anthony Ransford
# Modifications by Andrew Fisher (2017)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL.ImageQt import ImageQt
from PIL import Image
from PyQt4 import QtGui, QtCore
import numpy as np
from scipy.misc.pilutil import toimage
from scipy.optimize import curve_fit
import time, sys
import cv2
import re

class proflayout(QtGui.QWidget):

    def __init__(self):
        super(proflayout, self).__init__()
        self.zoom = 1
        #self.lowResFlag = False
        #self.highResFlag = False
        #self.mediumResFlag = False
        self.snapFlag = False
        self.imageres = [640,480]
        desktop = QtGui.QDesktopWidget()
        screensize = desktop.availableGeometry()
        self.screenres = [800,400]
        
        # initialize the camera
        self.camera = PiCamera()

        #set camera resolution, gain , sutter speed and framerate
        self.camera.resolution = (self.imageres[0], self.imageres[1])
        self.camera.framerate = 30 # in Hz
        self.camera.shutter_speed = 500 # in us
        self.camera.exposure_mode = 'off'
        self.camera.iso = 150

        #grab a reference to the raw camera capture
        self.rawCapture = PiRGBArray(self.camera, size=(self.imageres[0], self.imageres[1]))

        # allow the camera to warmup
        time.sleep(0.1)
        self.initializeGUI()

        
    def initializeGUI(self):

        #Initialization of Grid GUI
        self.setWindowTitle('Beam Profiler')
        self.setGeometry(0, 0, self.screenres[0], self.screenres[1])
        layout = QtGui.QGridLayout()

        #Initialize video window
        self.videowindow = QtGui.QLabel(self)

        #Initialize popup window
        self.warningmessage = QtGui.QMessageBox(self)
        self.warningmessage.resize(200,100)
        self.warningmessage.move(300,150)
        self.warningmessage.setText("")
        self.warningmessage.show()
        self.warningmessage.close()

        #Initialize buttons, textboxes, labels
        buttonsize = [150,100]
    
        self.pictextbox = QtGui.QLineEdit(self)
        self.pictextbox.resize(150,100)
        self.pictextbox.setPlaceholderText("Picture File Name ")

        self.matrixtextbox = QtGui.QLineEdit(self)
        self.matrixtextbox.resize(150,100)
        self.matrixtextbox.setPlaceholderText("Data Matrix File Name ")

        self.snapshotbutton = QtGui.QPushButton('Take Snapshot')
        self.snapshotbutton.setFixedSize(buttonsize[0],buttonsize[1])
        self.snapshotbutton.clicked.connect(self.setSnapFlag)

        #Initialization of resolution settings (working, unimplemented).
        
        #self.highresbutton = QtGui.QPushButton('High Res (1920x1080)')
        #self.mediumresbutton = QtGui.QPushButton('Med Res (1280x720)')
        #self.lowresbutton = QtGui.QPushButton('Low Res (640x480)')
        
        #self.highresbutton.setCheckable(True)
        #self.highresbutton.setChecked(True)
        #self.mediumresbutton.setCheckable(True)
        #self.lowresbutton.setCheckable(True)
        
        #self.highresbutton.setFixedSize(buttonsize[0],buttonsize[1])
        #self.mediumresbutton.setFixedSize(buttonsize[0],buttonsize[1])
        #self.lowresbutton.setFixedSize(buttonsize[0],buttonsize[1])

        #self.highresbutton.clicked.connect(self.highresFlagHandler)
        #self.mediumresbutton.clicked.connect(self.medresFlagHandler)
        #self.lowresbutton.clicked.connect(self.lowresFlagHandler)

        #Add buttons, video, textboxes to grid
                
        layout.addWidget(self.videowindow,   0,1,2,1)
        layout.addWidget(self.snapshotbutton, 0,0,2,1)
        #layout.addWidget(self.piclabel, 0,0,2,1)
        layout.addWidget(self.pictextbox, 1,0,2,1)
        #layout.addWidget(self.matrixlabel, 1,0,2,1)
        layout.addWidget(self.matrixtextbox, 2,0,2,1)
        #layout.addWidget(self.highresbutton, 1,0,2,1)
        #layout.addWidget(self.mediumresbutton, 2,0,2,1)
        #layout.addWidget(self.lowresbutton, 2,1,2,1)

        #Add grid to larger QWidget object
        self.setLayout(layout)

    def startCamera(self):
        # capture frames from the camera
        for frame in self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True):

            # grab the raw NumPy array representing the image, convert to greyscale by averaging RGB
            image = frame.array
            greyscaleImage = np.zeros((self.imageres[1], self.imageres[0]),dtype=np.float32)
            np.mean(image, axis=2, dtype=np.float32, out=greyscaleImage)
            

            #OpenCV initialization: needed for video rendering!
            key = cv2.waitKey(1) & 0xFF
            
            # convert RGB image np array to qPixmap and update video
            #converts nparray to qpixmap
            pilImage = toimage(greyscaleImage)
            qtImage = ImageQt(pilImage)
            qImage = QtGui.QImage(qtImage)
            qPixmap = QtGui.QPixmap(qImage)
            videoy = int(self.screenres[0]/2.1)
            videox = int(1.333 * videoy)
            self.videowindow.setPixmap(qPixmap.scaled(videox,videoy))

            #Breaks video capture loop if snapshot is being taken 
            if(self.snapFlag):
                break

            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)
            
        #Recursively restarts this function on completion 
        if(self.snapFlag):
            self.takeSnap()
            
    #def lowresFlagHandler(self):
     #   self.lowResFlag = True        

    #def medresFlagHandler(self):
     #   self.mediumResFlag = True

    #def highresFlagHandler(self):
     #   self.highResFlag = True
        
    #def lowres(self):
    #    self.highresbutton.setChecked(False)
     #   self.mediumresbutton.setChecked(False)
      #  self.imageres = [640, 480]
       # self.camera.resolution = (self.imageres[0], self.imageres[1])
        #self.rawCapture = PiRGBArray(self.camera, size=(self.imageres[0], self.imageres[1]))
        #self.lowResFlag = False
        #print('lowresswitch')
        #self.startCamera()
    
    #def highres(self):
     #   self.lowresbutton.setChecked(False)
      #  self.mediumresbutton.setChecked(False)
       # self.imageres = [1920,1088]
        #self.camera.resolution = (self.imageres[0], self.imageres[1])
        #self.rawCapture = PiRGBArray(self.camera, size=(self.imageres[0], self.imageres[1]))
        #self.highResFlag = False
        #print('highresswithc')
        #self.startCamera()

    #def mediumres(self):
     #   self.highresbutton.setChecked(False)
      #  self.lowresbutton.setChecked(False)
       # self.imageres = [1280,720]
        #self.camera.resolution = (self.imgres[0], self.imgres[1])
        #self.rawCapture = PiRGBArray(self.camera, size=(self.imgres[0], self.imgres[1]))
        #self.mediumResFlag = False
        #self('medresswitch')
        #self.startCamera()

    #Breaks video feed capture/display loop to prepare for static snapshot
    def setSnapFlag(self):
        self.snapFlag = True
        
    #Changes camera resolution, saves static image in greyscale.  Video feed pauses while this
        #executes
    def takeSnap(self):
        matchstring = re.compile('.txt|.png')
        isNotSaved = True

        #Change camera resolution
        self.camera.resolution = [3280, 2464]

        #Set taken image size
        imageDim = [1000,1000]

        #Grab image as numpyarray, convert to greyscale, save
        img = PiRGBArray(self.camera)
        self.camera.capture(img, format='rgb')
        greyscaleImage = np.zeros((self.camera.resolution[1],self.camera.resolution[0]), dtype=np.float)
        np.sum(img.array, axis=2, dtype=np.float32, out=greyscaleImage)
        greyscaleImage = greyscaleImage[(self.camera.resolution[0]-imageDim[0])/2:(self.camera.resolution[0]-imageDim[0])/2+imageDim[0], (self.camera.resolution[1]-imageDim[1])/2:(self.camera.resolution[1]-imageDim[1])/2+imageDim[1]]
        imgForSave = Image.fromarray(greyscaleImage.astype(np.uint8))
        
        if (re.search(matchstring, self.pictextbox.text())):
            imgForSave.save(self.pictextbox.text())
            isNotSaved = False
        elif(re.fullmatch('', self.pictextbox.text())):
            self.warningmessage.setText("Please type a filename for image export")
            self.warningmessage.open()
        else:
            imgForSave.save(self.pictextbox.text() + '.png')
            isNotSaved = False
        
        #Export greyscale image as data matrix
        np.set_printoptions(threshold=np.inf, linewidth=np.inf)

        
        if not (isNotSaved):
            if (re.search(matchstring, self.matrixtextbox.text())):
                self.warningmessage.setText('Data Exporting')
                self.warningmessage.open()
                with open(self.matrixtextbox.text(), 'w') as f:
                    f.write(np.array2string(greyscaleImage, separator=', '))
                isNotSaved = False
                self.warningmessage.close()
            elif(re.fullmatch('', self.matrixtextbox.text())):
                self.warningmessage.setText("Please type a filename for data export")
                self.warningmessage.open()
            else:
                self.warningmessage.setText('Data Exporting')
                self.warningmessage.open()
                with open(self.matrixtextbox.text() + ".txt", 'w') as f:
                    f.write(np.array2string(greyscaleImage, separator=', '))
                isNotSaved = False
                self.warningmessage.close()

        self.snapFlag = False

        #Reset resolution, clear capture, restart video feed
        self.camera.resolution = (self.imageres[0], self.imageres[1])
        self.rawCapture = PiRGBArray(self.camera, size=(self.imageres[0], self.imageres[1]))
        self.startCamera()

#Main function.  Runs program.
if __name__ == "__main__":

    a = QtGui.QApplication([])
    proflayoutwidget = proflayout()
    proflayoutwidget.show()
    proflayoutwidget.startCamera()

        
    sys.exit(a.exec_())


