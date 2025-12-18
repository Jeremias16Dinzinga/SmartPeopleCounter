import cv2

def start_camera(stream_url):
    cap = cv2.VideoCapture(stream_url)

    people_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("SmartPeopleCounter", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
