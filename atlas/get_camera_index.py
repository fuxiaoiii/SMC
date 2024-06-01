import cv2
ID = 0
while(ID<10000):
    cap = cv2.VideoCapture(ID)
    # get a frame
    ret, frame = cap.read()
    if ret == False:
        ID += 1
    else:
        print(ID)
        break
