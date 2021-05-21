import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from utils import intialize_predection_model
from upload import Ui_UploadImage
from realTime import Ui_RealTime
from randomGenerator import Ui_RandomGenerator

style_sheet = """QPushButton { background-color: #F76B8A;
                               color: #000000;
                               border-radius: 10px; }
QPushButton::hover { background-color: #ffffff;
                     color: #F76B8A;
                     border: 1px solid black; }
QPushButton::pressed { background-color: #000000;
                       color: #ffffff; }
QPushButton::disabled { background-color: rgba(255, 255, 255, 0.5);
                        color: #000000; }"""


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(850, 880)
        MainWindow.setMinimumSize(QtCore.QSize(850, 880))
        MainWindow.setStyleSheet("background-color: #ffffff;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(850, 850))
        self.centralwidget.setObjectName("centralwidget")
        self.main_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.main_layout.setObjectName("main_layout")

        self.game = QtWidgets.QFrame(self.centralwidget)
        self.game.setMinimumSize(QtCore.QSize(700, 700))
        self.game.setObjectName("game")
        self.game_layout = QtWidgets.QGridLayout(self.game)
        self.game_layout.setObjectName("game_layout")

        self.label = QtWidgets.QLabel(self.game)
        font = QtGui.QFont()
        font.setFamily("Goudy Stout")
        font.setPointSize(60)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #4592AF;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.game_layout.addWidget(self.label, 0, 0, 1, 1)
        self.main_layout.addWidget(self.game, 0, 0, 1, 1)
        self.options = QtWidgets.QWidget(self.centralwidget)
        self.options.setMinimumSize(QtCore.QSize(700, 90))
        self.options.setStyleSheet(style_sheet)
        self.options.setObjectName("options")
        self.options_layout = QtWidgets.QGridLayout(self.options)
        self.options_layout.setObjectName("options_layout")

        self.real_time_button = QtWidgets.QPushButton(self.options)
        self.real_time_button.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.real_time_button.setFont(font)
        self.real_time_button.setObjectName("real_time_button")
        self.options_layout.addWidget(self.real_time_button, 0, 0, 1, 1)

        self.upload_button = QtWidgets.QPushButton(self.options)
        self.upload_button.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.upload_button.setFont(font)
        self.upload_button.setStyleSheet("")
        self.upload_button.setObjectName("upload_button")
        self.options_layout.addWidget(self.upload_button, 0, 1, 1, 1)

        self.random_generator_button = QtWidgets.QPushButton(self.options)
        self.random_generator_button.setMinimumSize(QtCore.QSize(0, 80))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.random_generator_button.setFont(font)
        self.random_generator_button.setStyleSheet("")
        self.random_generator_button.setObjectName("random_generator_button")
        self.options_layout.addWidget(self.random_generator_button, 0, 2, 1, 1)
        self.main_layout.addWidget(self.options, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 850, 30))
        self.menubar.setMinimumSize(QtCore.QSize(0, 30))
        self.menubar.setStyleSheet("color: #000000;")
        self.menubar.setObjectName("menubar")
        self.instructions = QtWidgets.QMenu(self.menubar)
        self.instructions.setStyleSheet("")
        self.instructions.setObjectName("instructions")
        self.about = QtWidgets.QMenu(self.menubar)
        self.about.setObjectName("about")
        MainWindow.setMenuBar(self.menubar)
        self.menubar.addAction(self.instructions.menuAction())
        self.menubar.addAction(self.about.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Smart Sudoku"))
        self.label.setText(_translate("MainWindow", "SMART SUDOKU"))
        # buttons
        # ## real time
        self.real_time_button.setText(_translate("MainWindow", "Real time sudoku solver"))
        self.real_time_button.clicked.connect(lambda: self.start_game('realTime'))

        # ## upload
        self.upload_button.setText(_translate("MainWindow", "Upload a sudoku image"))
        self.upload_button.clicked.connect(lambda: self.start_game('upload'))

        # ## random generator
        self.random_generator_button.setText(_translate("MainWindow", "Generate a random game"))
        self.random_generator_button.clicked.connect(lambda: self.start_game('randomGenerator'))

        # menubar
        self.instructions.setTitle(_translate("MainWindow", "Instructions"))
        self.about.setTitle(_translate("MainWindow", "About"))

    def start_game(self, game):
        """Start game."""

        self.replace = QtWidgets.QWidget()
        self.replace.setMinimumSize(QtCore.QSize(700, 700))
        # adding to games frame
        self.game_layout.addWidget(self.replace, 0, 0, 1, 1)

        the_game = False

        if game == 'realTime':
            the_game = Ui_RealTime()

        elif game == 'upload':
            upload = QtWidgets.QWidget()
            ui = Ui_UploadImage()

            home_dir = str(os.getcwd())
            img = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', home_dir)

            model = intialize_predection_model('Resources/myModel.h5')

            ui.setupUi(upload, img[0], model)

            the_game = upload

        elif game == 'randomGenerator':
            randomGenerator = QtWidgets.QWidget()
            ui = Ui_RandomGenerator()
            ui.setupUi(randomGenerator)

            the_game = randomGenerator

        if the_game:
            self.game_layout.replaceWidget(self.replace, the_game)

def main():
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
