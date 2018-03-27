from PyQt5 import uic, QtWidgets
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QObject, QRect, Qt, QSize, QDate
from PyQt5.QtGui import QIcon
import sys

class Manager(QtWidgets.QDialog):
    def __init__(self, activity):
        super(Manager, self).__init__()
        uic.loadUi('../design/manager_view.ui', self)
        self.show()
        self.buttonPredict.clicked.connect(self.buttonPredictClicked)
        #self.buttonSendRobot.clicked.connect(self.buttonSendRobotClicked)
        self.activity_win = activity

    def callback_profileCompleted(self):
        self.activity.childProfile.close()
        if self.activity.childProfile.isprofileCompleted():
            #self.buttonProfile.setIcon(QIcon("../design/profil_G.png"))
            self.buttonProfile.setIconSize(QSize(100, 100))
            self.buttonPredict.setEnabled(True)

        date = "_" + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + "_" + str(datetime.now().hour) + "_" + str(datetime.now().minute)
        self.activity.pathWriter = PATH_DB + "/" + self.childProfile.lastName + "_" + self.activity.childProfile.firstName + date


    def buttonProfileClicked(self):
        self.activity.childProfile = ChildProfile(self.activity)
        self.activity.childProfile.signal_profileCompleted.connect(self.callback_profileCompleted)



    def buttonPredictClicked(self):
        #get letters from boxes
        trace = self.activity.tactileSurface.getData()
        boxes = self.activity.tactileSurface.boxesToDraw
        letters = self.activity.wt.separateWordsToLetters(trace, boxes, self.activity.tactileSurface.height(), self.activity.tactileSurface.convert_pix_meter)

        #compute score of all letters
        for index in letters:
            d_score = self.activity.predictor.predict(self.activity.childProfile.rightHanded,
            self.activity.childProfile.male,
            self.activity.childProfile.dateBirth.daysTo(QDate().currentDate())/30.5,
            self.activity.childProfile.section,
            letters[index],
            self.activity.lettersToWrite[index])

            self.activity.skills[self.activity.lettersToWrite[index]].dScore.append(d_score)


        #save data
        self.activity.saveData(letters)

        #update knowledge about dico
        self.activity.wt.updateWords(self.skills)

        #choose next word
        self.activity.algo()

        #clear screen
        self.activity.tactileSurface.eraseRobotTrace()
        self.activity.tactileSurface.erasePixmap()



    def buttonSendRobotClicked(self):

        data = self.activity.tactileSurface.data
        boxesCoordinates = self.activity.tactileSurface.boxesToDraw

        # create message containing path of word
        words_drawn = Path()

        for d in data:

            pose = PoseStamped()

            pose.pose.position.x = d.x*self.activity.tactileSurface.convert_pix_meter
            pose.pose.position.y = -d.y*self.activity.tactileSurface.convert_pix_meter + self.activity.tactileSurface.height()*self.activity.tactileSurface.convert_pix_meter# - boxesCoordinates[0][1]
            pose.header.seq = self.activity.seqWord
            words_drawn.poses.append(pose)

            self.activity.seqWord += 1

        words_drawn.header.stamp = rospy.get_rostime()

        # publish in topic
        self.activity.publish_word_written.publish(words_drawn)


        words_drawn = Path()
        words_drawn.header.stamp = rospy.get_rostime()
        self.activity.publish_word_written.publish(words_drawn)

        # clear screen
        self.activity.tactileSurface.eraseRobotTrace()
        self.activity.tactileSurface.erasePixmap()
