import cv2
import time
import asyncio
from ultralytics import YOLO
from tracker import CentroidTracker
from database import SessionLocal
from models import PeopleCount

STREAM_URL = "http://172.20.10.2:8080/video"
LINE_X = None
SAVE_INTERVAL = 1

model = YOLO("yolov8n.pt")
tracker = CentroidTracker()

def get_last_totals():
    db = SessionLocal()
    try:

        last_record = db.query(PeopleCount).order_by(PeopleCount.id.desc()).first()
        if last_record:
            return last_record.entered, last_record.exited, last_record.current_people
        else:
            return 0, 0, 0
    except Exception as e:
        print("Erro ao buscar últimos valores:", e)
        return 0, 0, 0
    finally:
        db.close()


def start_people_counter(manager, loop):
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        print("Erro ao abrir IP Webcam")
        return

    entered, exited, current_people = get_last_totals()
    crossed = {}
    last_saved_values = {"entered": -1, "exited": -1, "current": -1}
    last_save = time.time()
    alert_visible = True
    alert_timer = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        h, w, _ = frame.shape
        LINE_X = w // 2

        detections = []
        results = model(frame, conf=0.4, iou=0.5, verbose=False)

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    detections.append((cx, cy))

                    # Bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        objects, previous = tracker.update(detections)

        for oid, (cx, cy) in objects.items():
            prev_pos = previous.get(oid, (cx, cy))
            prev_cx, prev_cy = prev_pos

            if oid not in crossed:
                crossed[oid] = None

            # ENTRADA → esquerda para direita
            if prev_cx < LINE_X <= cx and crossed[oid] != "right":
                entered += 1
                crossed[oid] = "right"

            # SAÍDA → direita para esquerda
            elif prev_cx > LINE_X >= cx and crossed[oid] != "left":
                exited += 1
                crossed[oid] = "left"

            # ID
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"ID {oid}", (cx - 15, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        current_people = max(0, entered - exited)

        # Linha virtual vertical
        cv2.line(frame, (LINE_X, 0), (LINE_X, frame.shape[0]), (255, 0, 0), 2)

        # Contadores no vídeo
        cv2.putText(frame, f"Entradas: {entered}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Saidas: {exited}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, f"Atual: {current_people}", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # ALERTA DE ENTRADA SUSPEITA
        alert_msg = ""
        if exited > entered:
            alert_msg = f"ALERTA: {exited - entered} Entrada suspeita detectada!"

            if time.time() - alert_timer > 0.5:
                alert_visible = not alert_visible
                alert_timer = time.time()

            if alert_visible:
                cv2.putText(frame, alert_msg, (20, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

        asyncio.run_coroutine_threadsafe(
            manager.broadcast({
                "entered": entered,
                "exited": exited,
                "current": current_people,
                "alert": alert_msg
            }),
            loop
        )

        if ((entered != last_saved_values["entered"] or
            exited != last_saved_values["exited"] or
            current_people != last_saved_values["current"]) and
            (time.time() - last_save >= SAVE_INTERVAL)):

            db = SessionLocal()
            try:
                db.add(PeopleCount(
                    entered=entered,
                    exited=exited,
                    current_people=current_people
                ))
                db.commit()
                # Atualiza últimos valores salvos e tempo
                last_saved_values["entered"] = entered
                last_saved_values["exited"] = exited
                last_saved_values["current"] = current_people
                last_save = time.time()
            except Exception as e:
                db.rollback()
                print("DB erro:", e)
            finally:
                db.close()

        cv2.imshow("SmartPeopleCounter - IP Webcam", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
