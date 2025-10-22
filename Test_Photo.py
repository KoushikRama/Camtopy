import cv2
import random
camw = 1080
camh = 1920

cam = cv2.VideoCapture(0)
pic_no = 0
while True:
    ret , frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Camera",frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        filename = f'photo{random.randint(1,1000000000000)}.jpg'
        cv2.imwrite(filename,frame)
        print("photo Saved to ",filename)
    elif key == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()