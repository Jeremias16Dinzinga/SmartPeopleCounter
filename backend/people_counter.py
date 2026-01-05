import cv2
import time
from ultralytics import YOLO
from tracker import CentroidTracker
from database import SessionLocal
from models import PeopleCount

model = YOLO("yolov8n.pt")
model.verbose = False
tracker = CentroidTracker()

LINE_Y = 300
SAVE_INTERVAL = 60  # segundos


def start_people_counter(stream_url):
    cap = cv2.VideoCapture(stream_url)
    #cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro ao abrir a câmera")
        return
    
    entered = 0
    exited = 0
   
    last_save = time.time()
   
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = []

        # Inferência YOLO
        results = model(frame, stream=True)

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:  # pessoa
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    detections.append((cx, cy))

                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 0, 255), 2)
        
        objects, previous = tracker.update(detections)

        for object_id, (cx, cy) in objects.items():
            prev_cy = previous.get(object_id, cy)

            # Entrada
            if prev_cy < LINE_Y and cy >= LINE_Y:
                entered += 1

            # Saída
            elif prev_cy > LINE_Y and cy <= LINE_Y:
                exited += 1

            cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)
            cv2.putText(frame, f"ID {object_id}",
                        (cx - 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)

        # Linha virtual
        cv2.line(frame, (0, LINE_Y),
                 (frame.shape[1], LINE_Y),
                 (255, 0, 0), 2)

        # Contadores
        cv2.putText(frame, f"Entradas: {entered}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        cv2.putText(frame, f"Saidas: {exited}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Guardar no MySQL por intervalo
        if time.time() - last_save >= SAVE_INTERVAL:
            db = SessionLocal()
            total = entered - exited
            db.add(PeopleCount(count=total))
            db.commit()
            db.close()
            last_save = time.time()

        cv2.imshow("SmartPeopleCounter - YOLOv8", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
