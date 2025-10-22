import cv2

cap = cv2.VideoCapture(0)
w = int(cap.get(3))
h = int(cap.get(4))

output = cv2.VideoWriter("FirstRec.avi",cv2.VideoWriter_fourcc(*'mp4v'),20,(w,h))
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    output.write(frame)
    cv2.imshow("Webcam Recording ...",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()