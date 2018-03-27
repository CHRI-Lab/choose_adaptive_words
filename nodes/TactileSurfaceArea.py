from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen, QPixmap, QTabletEvent
from PyQt5.QtCore import QPoint, pyqtSignal, Qt, QTime
from nav_msgs.msg import Path
import rospy

from Data import Data

SIZE_ROBOT_WRITING = 4.0
DISTANCE_ROBOT_WRITING_TO_TOP = 50
DISTANCE_BOX_TO_BOTTOM = 100
SIZE_BOXES = 6.0
TIME_BTW_POINTS = 0.03
TIME_PEN_UP = 0.2

class TactileSurfaceArea(QTableWidget):

	signalRobotFinishWriting = pyqtSignal()

	def __init__(self, parent = None):
		QTableWidget.__init__(self, parent)

		self.myBrush = QBrush()
		self.myPen = QPen()
		self.pixmap = None
		self.pixmapHandwriting = None
		self.deviceDown = False
		self.time = QTime()
		self.lastPoints = [QPoint(), QPoint()]
		self.boxesToDraw = []
		self.data = []
		self.convert_pix_meter = 0.0001534

		self.initPixmaps()
		self.setAutoFillBackground(True)
		self.setCursor(Qt.BlankCursor)
		self.time.start()

	def initPixmaps(self):
		width = 8000
		height = 8000

		self.pixmap = QPixmap(width, height)
		self.pixmap.fill(QColor(255, 255, 255))

		self.pixmapHandwriting = QPixmap(width, height)
		self.pixmapHandwriting.fill(QColor(255, 255, 255))

		self.viewport().update()

	def paintEvent(self, event):
		p = QPainter()
		p.begin(self.viewport())
		p.drawPixmap(0, 0, self.pixmap)
		p.drawPixmap(0, 0, self.pixmapHandwriting)
		p.end()

	def tabletEvent(self, event):
		if event.type() == QTabletEvent.TabletPress:
			if self.deviceDown == False:
				self.deviceDown = True
				self.lastPoints[0] = event.pos()
				self.lastPoints[1] = event.pos()

		elif event.type() == QTabletEvent.TabletRelease:
			if self.deviceDown:
				self.deviceDown = False

		elif event.type() == QTabletEvent.TabletMove:
			self.lastPoints[1] = self.lastPoints[0]
			self.lastPoints[0] = event.pos()

			if self.deviceDown:
				self.updateBrush(event)
				painter = QPainter(self.pixmapHandwriting)
				self.paintPixmap(painter, event)
				self.data.append(Data(self.time.elapsed(), event.posF().x(), event.posF().y(), event.xTilt(), event.yTilt(), event.pressure()))

	def updateBrush(self, event):
		#hue, saturation, value, alpha;
		#myColor.getHsv(&hue, &saturation, &value, &alpha)
		myColor = QColor()

		vValue = int(((event.yTilt() + 60.0) / 120.0) * 255)
		hValue = int(((event.xTilt() + 60.0) / 120.0) * 255)
		alpha = int(event.pressure() * 255.0)

		# print vValue, hValue,alpha

		myColor.setHsv(0, vValue, hValue, alpha)
		#myColor.setAlpha(alpha)

		self.myPen.setWidthF(event.pressure() * 2 + 1)
		self.myBrush.setColor(myColor)
		self.myPen.setColor(myColor)

	def paintPixmap(self, painter, event):

		painter.setBrush(self.myBrush)
		painter.setPen(self.myPen)
		painter.drawLine(self.lastPoints[1], event.pos())
		self.viewport().update()

	def erasePixmap(self):

		newPixmap = QPixmap(self.width(), self.height())
		newPixmap.fill(QColor(255, 255, 255, 0))
		self.pixmapHandwriting = newPixmap
		painter = QPainter(self.pixmap)
		painter.drawPixmap(0, 0, self.pixmapHandwriting)
		painter.end()

		# update drawing
		self.viewport().update()

		# erase data
		self.data = []

		# restart timer
		self.time.start()

	def eraseRobotTrace(self):

		newPixmap = QPixmap(self.width(), self.height())
		newPixmap.fill(QColor(255, 255, 255, 0))
		self.pixmap = newPixmap
		painter = QPainter(self.pixmap)
		painter.drawPixmap(0, 0, self.pixmap)
		painter.end()

		# update drawing
		self.viewport().update()

		# erase data
		self.data = []

		# restart timer
		self.time.start()

	def drawWord(self, path):
		# prepare drawing
		painter = QPainter(self.pixmap)


		myColor = QColor(0, 0, 0)
		self.myBrush.setColor(myColor)
		self.myPen.setColor(myColor)
		self.myPen.setWidthF(SIZE_ROBOT_WRITING)
		painter.setBrush(self.myBrush)
		painter.setPen(self.myPen)

		x = []
		y = []
		penUp = []
		t = []
		for i, pose in enumerate(path.poses):
			x.append(float(pose.pose.position.x) / self.convert_pix_meter)
			y.append(float(pose.pose.position.y) / self.convert_pix_meter)
			penUp.append(pose.header.seq)
			t.append(pose.header.stamp.nsecs)


		# put y in touch pad coordinate
		y = [-y_ + min(y) + max(y) for y_ in y]

		# put word in top of screen
		y = [y_- min(y) + DISTANCE_ROBOT_WRITING_TO_TOP for y_ in y]

		# wait that robot move its arm up
		rospy.sleep(3.)

		# draw
		for i in range(len(x)):
			if i > 1:
				if penUp[i] == 0 and penUp[i-1] == 0:
					painter.drawLine(QPoint(x[i-1], y[i-1]), QPoint(x[i], y[i]))
					self.viewport().update()
					waitingTime = (t[i] - t[i -1])/1000000.0
					rospy.sleep(TIME_BTW_POINTS)
				else:
					rospy.sleep(TIME_PEN_UP)

		# advert that drawing is done
		self.signalRobotFinishWriting.emit()

	def drawBoxes(self):
		# prepare drawing
		painter = QPainter(self.pixmap)

		myColor = QColor(0, 0, 0)
		self.myBrush.setColor(myColor)
		self.myPen.setColor(myColor)
		self.myPen.setWidthF(SIZE_BOXES)
		painter.setBrush(self.myBrush)
		painter.setPen(self.myPen)

		for data in self.boxesToDraw:

			x = data[0]/self.convert_pix_meter
			y = self.height() - data[1]/self.convert_pix_meter

			width = data[2]/self.convert_pix_meter - data[0]/self.convert_pix_meter
			height = -data[3]/self.convert_pix_meter + data[1]/self.convert_pix_meter

			painter.drawRect(x, y, width, height)
			self.viewport().update()


	def getData(self):
		return self.data
