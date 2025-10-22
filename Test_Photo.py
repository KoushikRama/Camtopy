import cv2
import random

cam = cv2.VideoCapture(0) # Starting the Camera
while True:
    ret , frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Camera",frame)
    key = cv2.waitKey(1) & 0xFF # key checks the return value
    if key == ord('c'):
        filename = f'photo{random.randint(1,1000000000000)}.jpg' # To ensure every photo generated has a unique name
        cv2.imwrite(filename,frame)
        print("photo Saved to ",filename)
    elif key == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()