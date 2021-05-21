from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import numpy as np
import utils
import sudukoSolver

style_sheet = """QTabBar::tab { background-color: #ffffff;
                                color: #000000;
                                padding: 7px;
                                border: 1px solid black; }
QTabBar::tab::hover { background-color: rgba(255, 255, 255, 0.8); }
QTabBar::tab::selected { background-color: #000000;
                         color: #ffffff; }"""


class Ui_UploadImage(object):
    def setupUi(self, UploadImage, img, model):
        # uploaded image
        self.img_path = img
        # digit recognition model
        self.model = model

        UploadImage.setObjectName("UploadImage")
        UploadImage.resize(700, 700)
        UploadImage.setMinimumSize(QtCore.QSize(700, 700))
        UploadImage.setStyleSheet("background-color: #ffffff;")
        self.main_layout = QtWidgets.QGridLayout(UploadImage)
        self.main_layout.setObjectName("main_layout")

        self.tab_widget = QtWidgets.QTabWidget(UploadImage)
        self.tab_widget.setMinimumSize(QtCore.QSize(600, 600))
        font = QtGui.QFont()
        font.setFamily("Lucida Sans Typewriter")
        font.setPointSize(10)
        self.tab_widget.setFont(font)
        self.tab_widget.setStyleSheet(style_sheet)
        self.tab_widget.setUsesScrollButtons(False)
        self.tab_widget.setObjectName("tab_widget")

        self.unsolved_tab = QtWidgets.QWidget()
        self.unsolved_tab.setStyleSheet("")
        self.unsolved_tab.setObjectName("unsolved_tab")
        self.unsolved_layout = QtWidgets.QGridLayout(self.unsolved_tab)
        self.unsolved_layout.setObjectName("unsolved_layout")
        self.unsolved_image = QtWidgets.QLabel(self.unsolved_tab)
        self.unsolved_image.setMinimumSize(QtCore.QSize(600, 600))
        self.unsolved_image.setPixmap(QtGui.QPixmap(self.img_path))
        self.unsolved_image.setScaledContents(True)
        self.unsolved_image.setObjectName("unsolved_image")
        self.unsolved_layout.addWidget(self.unsolved_image, 0, 0, 1, 1)
        self.tab_widget.addTab(self.unsolved_tab, "")

        self.solved_tab = QtWidgets.QWidget()
        self.solved_tab.setObjectName("solved_tab")
        self.solved_layout = QtWidgets.QGridLayout(self.solved_tab)
        self.solved_layout.setObjectName("solved_layout")
        self.solved_image = QtWidgets.QLabel(self.solved_tab)
        self.solved_image.setMinimumSize(QtCore.QSize(600, 600))
        self.solved_image.setScaledContents(True)
        self.solved_image.setObjectName("solved_image")
        self.solved_layout.addWidget(self.solved_image, 0, 0, 1, 1)
        self.tab_widget.addTab(self.solved_tab, "")
        self.main_layout.addWidget(self.tab_widget, 0, 0, 1, 1)

        self.retranslateUi(UploadImage)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(UploadImage)

    def retranslateUi(self, UploadImage):
        _translate = QtCore.QCoreApplication.translate

        self.tab_widget.setTabText(self.tab_widget.indexOf(self.unsolved_tab), _translate("UploadImage", "Unsolved"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.solved_tab), _translate("UploadImage", "Solution"))
        self.solved_image.setText(_translate("UploadImage", "Solving Sudoku..."))
        self.sudoku_main()
    
    def sudoku_main(self):
        heightImg = 450
        widthImg = 450

        # #### 1. prepare the image ################################################################
        self.img = cv2.imread(self.img_path)
        self.img = cv2.resize(self.img, (widthImg, heightImg))

        self.imgThreshold = utils.pre_process(self.img)

        # #### 2. find biggest out of all contours #################################################
        contours, _ = cv2.findContours(
            self.imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        biggest, _ = utils.biggest_contour(contours)

        if biggest.size != 0:
            biggest = utils.reorder(biggest)

            pts1 = np.float32(biggest)
            pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [
                            widthImg, heightImg]])

            matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GER
            self.imgWarpColored = cv2.warpPerspective(self.img, matrix, (widthImg, heightImg))
            self.imgWarpColored = cv2.cvtColor(self.imgWarpColored, cv2.COLOR_BGR2GRAY)

            # #### 3. split the image and find digits ##############################################
            self.imgSolvedDigits = np.zeros((heightImg, widthImg, 3), np.uint8)
            boxes = utils.split_boxes(self.imgWarpColored)

            numbers = utils.get_prediction(boxes, self.model)
            numbers = np.asarray(numbers)

            # 1 for empty cells, 0 for filled cells
            posArray = np.where(numbers > 0, 0, 1)

            # #### 4. find solution ################################################################
            # converting to our board format
            board = np.array_split(numbers, 9)

            # try to find solution if one exists
            try:
                sudukoSolver.solve(board)
            except:
                pass

            flatList = []
            for sublist in board:
                for item in sublist:
                    flatList.append(item)
            solvedNumbers = flatList*posArray
            self.imgSolvedDigits = utils.display_numbers(self.imgSolvedDigits, solvedNumbers)

            # overlay solution
            # warp
            pts2 = np.float32(biggest)
            pts1 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            self.imgInvWarpColored = self.img.copy()
            self.imgInvWarpColored = cv2.warpPerspective(self.imgSolvedDigits, matrix, (widthImg, heightImg))
            self.inv_perspective = cv2.addWeighted(self.imgInvWarpColored, 1, self.img, 0.5, 1)
            cv2.imwrite("solved.jpg", self.inv_perspective)

            self.solved_image.setPixmap(QtGui.QPixmap("solved.jpg"))
