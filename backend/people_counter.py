import cv2
import time
import asyncio
from ultralytics import YOLO
from tracker import CentroidTracker
from database import SessionLocal
from models import PeopleCount

# Carregar modelo YOLOv8
model = YOLO("yolov8n.pt")
model.verbose = False

# Tracker de centroides
tracker = CentroidTracker()

# Linha virtual
LINE_Y = 300

# Intervalo para salvar no MySQL (em segundos)
SAVE_INTERVAL = 60


def start_people_counter(stream_url, manager, loop):
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        print("Erro ao abrir a câmera")
        return

    entered = 0
    exited = 0
    last_save = time.time()
    last_saved_people = -1  # controla gravação somente se houver mudança

    already_crossed = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            # Se a câmera falhar momentaneamente, continuar
            time.sleep(0.01)
            continue

        detections = []

        # Inferência YOLO
        results = model(frame, stream=True)

        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:  # classe 0 = pessoa
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    detections.append((cx, cy))

        # Atualiza rastreamento
        objects, previous = tracker.update(detections)

        # Contagem por linha
        for object_id, (cx, cy) in objects.items():
            prev_cy = previous.get(object_id, cy)

            if object_id not in already_crossed:
                already_crossed[object_id] = None

            # Entrada
            if prev_cy < LINE_Y and cy >= LINE_Y and already_crossed[object_id] != "down":
                entered += 1
                already_crossed[object_id] = "down"

            # Saída
            elif prev_cy > LINE_Y and cy <= LINE_Y and already_crossed[object_id] != "up":
                exited += 1
                already_crossed[object_id] = "up"

        # Total de pessoas atuais (nunca negativo)
        current_people = max(0, entered - exited)

        # Enviar dados para frontend em tempo real
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({
                "entered": entered,
                "exited": exited,
                "current_people": current_people
            }),
            loop
        )

        # Gravar no MySQL somente se houver alteração
        if time.time() - last_save >= SAVE_INTERVAL:
            if current_people != last_saved_people:
                db = SessionLocal()
                try:
                    db.add(PeopleCount(
                        entered=entered,
                        exited=exited,
                        current_people=current_people
                    ))
                    db.commit()
                    last_saved_people = current_people
                except Exception as e:
                    print("Erro ao gravar no MySQL:", e)
                    db.rollback()
                finally:
                    db.close()
            last_save = time.time()

        # Pequeno delay para reduzir uso de CPU
        time.sleep(0.01)
