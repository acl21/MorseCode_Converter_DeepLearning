from morse_converter import MorseConverter as mc
from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2

# Thresholds and consecutive frame length for triggering the mouse action.
EYE_AR_THRESH = 0.19
EYE_AR_CONSECUTIVE_FRAMES = 15
WINK_AR_DIFF_THRESH = 0.04
WINK_AR_CLOSE_THRESH = 0.19
WINK_CONSECUTIVE_FRAMES = 10

# Initialize the frame counters for each action as well as
# booleans used to indicate if action is performed or not

EYE_COUNTER = 0
WINK_COUNTER = 0
INPUT_MODE = False
EYE_CLICK = False
LEFT_WINK = False
RIGHT_WINK = False

WHITE_COLOR = (255, 255, 255)
YELLOW_COLOR = (0, 255, 255)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 255, 0)
BLUE_COLOR = (255, 0, 0)
BLACK_COLOR = (0, 0, 0)

WINK_EYE = ''
INPUT = ''
MESSAGE = ''
CONVERTED_MSG = ''

# Initialize Dlib's face detector (HOG-based) and then initialize
# the facial landmark predictor
shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

# Grab the indexes of the facial landmarks for the left and
# right eye respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


# Returns EAR given eye landmarks
def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])

    # Compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = np.linalg.norm(eye[0] - eye[3])

    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # Return the eye aspect ratio
    return ear


# Video capture
vid = cv2.VideoCapture(0)
resolution_w = 1366
resolution_h = 768
cam_w = 640
cam_h = 480
unit_w = resolution_w / cam_w
unit_h = resolution_h / cam_h

while True:
    # Grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale
    # channels)
    _, frame = vid.read()
    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=cam_w, height=cam_h)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    rect = detector(gray, 0)

    # Loop over the face detections
    if len(rect) > 0:
        rect = rect[0]
    else:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        continue

    # Determine the facial landmarks for the face region, then
    # convert the facial landmark (x, y)-coordinates to a NumPy
    # array
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    # Extract the left and right eye coordinates, then use the
    # coordinates to compute the eye aspect ratio for both eyes
    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    # Because I flipped the frame, left is right, right is left.
    temp = leftEye
    leftEye = rightEye
    rightEye = temp

    # Average the mouth aspect ratio together for both eyes
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    diff_ear = np.abs(leftEAR - rightEAR)

    # Compute the convex hull for the left and right eye, then
    # visualize each of the eyes
    leftEyeHull = cv2.convexHull(leftEye)
    rightEyeHull = cv2.convexHull(rightEye)
    cv2.drawContours(frame, [leftEyeHull], -1, YELLOW_COLOR, 1)
    cv2.drawContours(frame, [rightEyeHull], -1, YELLOW_COLOR, 1)

    for (x, y) in np.concatenate((leftEye, rightEye), axis=0):
        cv2.circle(frame, (x, y), 2, GREEN_COLOR, -1)

    # Check to see if the eye aspect ratio is below the blink
    # threshold, and if so, increment the blink frame counter
    if diff_ear > WINK_AR_DIFF_THRESH:

        # Check for Left Wink
        if leftEAR < rightEAR:
            if leftEAR < EYE_AR_THRESH:
                WINK_COUNTER += 1

                if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                    cv2.putText(frame, 'Release Now For: Back Space', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
                    WINK_EYE = 'LEFT'

        # Check for Right Wink
        elif leftEAR > rightEAR:
            if rightEAR < EYE_AR_THRESH:
                WINK_COUNTER += 1

                if WINK_COUNTER > WINK_CONSECUTIVE_FRAMES:
                    cv2.putText(frame, 'Release Now For: Space', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
                    WINK_EYE = 'RIGHT'

    elif WINK_EYE != '':
        if WINK_EYE == 'LEFT':
            # Back Space
            MESSAGE = MESSAGE.split('*')
            MESSAGE = MESSAGE[:-1]
            MESSAGE = '*'.join(MESSAGE)
        elif WINK_EYE == 'RIGHT':
            MESSAGE += '*'
        WINK_COUNTER = 0
        WINK_EYE = ''

    else:
        if ear <= EYE_AR_THRESH:
            EYE_COUNTER += 1
            if (EYE_COUNTER > EYE_AR_CONSECUTIVE_FRAMES) and (EYE_COUNTER < 2 * EYE_AR_CONSECUTIVE_FRAMES):
                cv2.putText(frame, 'Release Now For: DOT', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
            elif EYE_COUNTER >= 3 * EYE_AR_CONSECUTIVE_FRAMES:
                    cv2.putText(frame, 'Release Now For: DASH', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED_COLOR, 2)
        else:
            if EYE_COUNTER > EYE_AR_CONSECUTIVE_FRAMES:
                if EYE_COUNTER > 3 * EYE_AR_CONSECUTIVE_FRAMES:
                    INPUT = '-'
                else:
                    INPUT = '.'
            EYE_COUNTER = 0
            WINK_COUNTER = 0

    MESSAGE += INPUT
    INPUT = ''
    # Show EAR and Diff_EAR for reference
    cv2.putText(frame, "Right EAR: {:.2f}".format(rightEAR), (460, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW_COLOR, 2)
    cv2.putText(frame, "Left EAR: {:.2f}".format(leftEAR), (460, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW_COLOR, 2)
    cv2.putText(frame, "Diff EAR: {:.2f}".format(np.abs(leftEAR - rightEAR)), (460, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW_COLOR, 2)

    # Show the morse code and the converted text
    cv2.putText(frame, "Morse Code: " + MESSAGE, (40, 420),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW_COLOR, 2)
    if MESSAGE != '' and MESSAGE[-1] == '*':
        CONVERTED_MSG = mc._morseToText(MESSAGE)

    cv2.putText(frame, "Converted Text: " + CONVERTED_MSG, (40, 460),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW_COLOR, 2)

    # Show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If the `Esc` key was pressed, break from the loop
    if key == 27:
        break

# Do a bit of cleanup
cv2.destroyAllWindows()
vid.release()
