import cv2

video_path = '../rawdata/20201211_131147.mp4'
cap = cv2.VideoCapture(video_path)
while True:
    pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
    frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
    frame_exists, _ = cap.read()
    if not frame_exists:
        break
    print(frame_number, pos_msec, frame_exists)
cap.release()