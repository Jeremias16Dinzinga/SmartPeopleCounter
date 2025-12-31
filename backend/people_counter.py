import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.verbose = False

def start_people_counter(stream_url):
    cap = cv2.VideoCapture(stream_url)
    #cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro ao abrir a câmera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Inferência YOLO
        results = model(frame, stream=True)

        people_count = 0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])

                # Classe 0 = pessoa
                if cls == 0:
                    people_count += 1

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Desenhar bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 0, 255), 2)

                    cv2.putText(frame, "Pessoa",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0, 0, 255), 2)

        # Mostrar contador
        cv2.putText(frame, f"Pessoas: {people_count}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 3)

        cv2.imshow("SmartPeopleCounter - YOLOv8", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
