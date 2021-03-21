"""Main project to solve the sudoku using OpenCV and backtracking."""

from utlis import *
import sudukoSolver
import os
# INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# choosing image to be solved
num = int(input("Enter image (1-3): "))
pathImage = f"Resources/{num}.jpg"
heightImg = 450
widthImg = 450

# loading the model
model = intializePredectionModel()

# #### 1. prepare the image ################################################################
img = cv2.imread(pathImage)
img = cv2.resize(img, (widthImg, heightImg))

# blank image for testing/debugging
imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)

imgThreshold = preProcess(img)

# #### 2. find all contours ################################################################
imgContours = img.copy()
imgBigContour = img.copy()

contours, hierarchy = cv2.findContours(
    imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 3)

# find the biggest contour (the sudoku board)
biggest, maxArea = biggestContour(contours)
# if sudoku exists
if biggest.size != 0:
    biggest = reorder(biggest)
    cv2.drawContours(imgBigContour, biggest, -1, (0, 0, 255),
                     25)

    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [
                      widthImg, heightImg]])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GER
    imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    imgDetectedDigits = imgBlank.copy()
    imgWarpColored = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)

    # #### 3. split the image and find digits ################################################################
    imgSolvedDigits = imgBlank.copy()
    boxes = splitBoxes(imgWarpColored)

    numbers = getPredection(boxes, model)

    imgDetectedDigits = displayNumbers(
        imgDetectedDigits, numbers, color=(255, 0, 255))
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
    imgSolvedDigits = displayNumbers(imgSolvedDigits, solvedNumbers)

    # overlay solution
    # warp
    pts2 = np.float32(biggest)
    pts1 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [
                      widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgInvWarpColored = img.copy()
    imgInvWarpColored = cv2.warpPerspective(
        imgSolvedDigits, matrix, (widthImg, heightImg))
    inv_perspective = cv2.addWeighted(imgInvWarpColored, 1, img, 0.5, 1)

    # drawing grid
    imgDetectedDigits = drawGrid(imgDetectedDigits)
    imgSolvedDigits = drawGrid(imgSolvedDigits)

    imageArray = ([img, imgThreshold, imgContours, imgBigContour],
                  [imgDetectedDigits, imgSolvedDigits, imgInvWarpColored, inv_perspective])
    stackedImage = stackImages(imageArray, 1)
    cv2.imshow('Stacked Images', stackedImage)

else:
    print("No Sudoku Found")

cv2.waitKey(0)
