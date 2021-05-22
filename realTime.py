import cv2
import numpy as np
import operator
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from utils import intialize_predection_model
import realtime_sol as sol

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    finalPixmap = pyqtSignal(QImage)

    def run(self):
        global running

        model = intialize_predection_model("Resources/digit_model.h5")
        margin = 4
        box = 28 + 2 * margin
        grid_size = 9 * box
        flag = 0
        count = 0

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while running:
            ret, frame = cap.read()
            if ret:
                # image preprocessing
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (7, 7), 0)
                thresh = cv2.adaptiveThreshold(
                    gray,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY_INV,
                    9,
                    2,
                )

                # finding biggest contour
                contours, _ = cv2.findContours(
                    thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
                )
                grid_contour = None
                maxArea = 0

                for c in contours:
                    area = cv2.contourArea(c)
                    if area > 25000:
                        perimeter = cv2.arcLength(c, True)
                        polygon = cv2.approxPolyDP(c, 0.01 * perimeter, True)
                        if area > maxArea and len(polygon) == 4:
                            grid_contour = polygon
                            maxArea = area

                # finding points
                if grid_contour is not None:
                    cv2.drawContours(frame, [grid_contour], 0, (0, 255, 0), 2)
                    points = np.vstack(grid_contour).squeeze()
                    points = sorted(points, key=operator.itemgetter(1))
                    if points[0][0] < points[1][0]:
                        if points[3][0] < points[2][0]:
                            pts1 = np.float32(
                                [points[0], points[1], points[3], points[2]]
                            )
                        else:
                            pts1 = np.float32(
                                [points[0], points[1], points[2], points[3]]
                            )
                    else:
                        if points[3][0] < points[2][0]:
                            pts1 = np.float32(
                                [points[1], points[0], points[3], points[2]]
                            )
                        else:
                            pts1 = np.float32(
                                [points[1], points[0], points[2], points[3]]
                            )
                    pts2 = np.float32(
                        [[0, 0], [grid_size, 0], [0, grid_size], [grid_size, grid_size]]
                    )

                    M = cv2.getPerspectiveTransform(pts1, pts2)
                    grid = cv2.warpPerspective(frame, M, (grid_size, grid_size))
                    grid = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY)
                    grid = cv2.adaptiveThreshold(
                        grid,
                        255,
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        cv2.THRESH_BINARY_INV,
                        7,
                        3,
                    )

                    # cv2.imshow("hehe", grid)
                    if flag == 0:
                        grid_text = []
                        for y in range(9):
                            ligne = ""
                            for x in range(9):
                                y2min = y * box + margin
                                y2max = (y + 1) * box - margin
                                x2min = x * box + margin
                                x2max = (x + 1) * box - margin

                                img = grid[y2min:y2max, x2min:x2max]
                                x = img.reshape(1, 28, 28, 1)
                                if x.sum() > 10000:
                                    prediction = model.predict_classes(x)
                                    ligne += "{:d}".format(prediction[0])
                                else:
                                    ligne += "{:d}".format(0)
                            grid_text.append(ligne)
                        result = sol.sudoku(grid_text)

                    if result is not None:
                        count += 1
                        flag = 1
                        fond = np.zeros(
                            shape=(grid_size, grid_size, 3), dtype=np.float32
                        )
                        for y in range(len(result)):
                            for x in range(len(result[y])):
                                if grid_text[y][x] == "0":
                                    cv2.putText(
                                        fond,
                                        "{:d}".format(result[y][x]),
                                        (
                                            (x) * box + margin + 3,
                                            (y + 1) * box - margin - 3,
                                        ),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        1,
                                        (255, 0, 0),
                                        2,
                                    )
                        M = cv2.getPerspectiveTransform(pts2, pts1)

                        h, w, c = frame.shape
                        fondP = cv2.warpPerspective(fond, M, (w, h))
                        img2gray = cv2.cvtColor(fondP, cv2.COLOR_BGR2GRAY)
                        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
                        mask = mask.astype("uint8")
                        mask_inv = cv2.bitwise_not(mask)
                        img1_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
                        img2_fg = cv2.bitwise_and(fondP, fondP, mask=mask).astype(
                            "uint8"
                        )
                        dst = cv2.add(img1_bg, img2_fg)
                        print("count", count)
                        if count >= 3:
                            running = False
                            self.show_frame(dst)

                    else:
                        self.show_frame(frame)

                else:
                    flag = 0
                    self.show_frame(frame)

    def show_frame(self, frame):
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        QtFormat = QImage(
            rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888
        )
        if running:
            self.changePixmap.emit(QtFormat)
        else:
            self.finalPixmap.emit(QtFormat)

class Ui_RealTime(QtWidgets.QWidget):
    def __init__(self, is_on):
        super().__init__()

        global running
        running = is_on
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.feed.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.resize(700, 700)
        self.setMinimumSize(QtCore.QSize(700, 700))
        self.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.feed = QtWidgets.QLabel(self)
        self.feed.setMinimumSize(QtCore.QSize(680, 680))
        self.feed.setScaledContents(True)
        self.feed.setObjectName("feed")
        self.gridLayout.addWidget(self.feed, 0, 0, 1, 1)
        
        if running:
            th = Thread(self)
            th.changePixmap.connect(self.setImage)
            th.finalPixmap.connect(self.setImage)
            th.start()
