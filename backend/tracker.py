import math

class CentroidTracker:
    def __init__(self, max_distance=50):
        self.next_id = 0
        self.objects = {}      
        self.previous = {}     
        self.max_distance = max_distance

    def update(self, detections):
        updated_objects = {}

        for cx, cy in detections:
            matched = False

            for object_id, (ox, oy) in self.objects.items():
                distance = math.hypot(cx - ox, cy - oy)

                if distance < self.max_distance:
                    updated_objects[object_id] = (cx, cy)
                    self.previous[object_id] = oy
                    matched = True
                    break

            if not matched:
                updated_objects[self.next_id] = (cx, cy)
                self.previous[self.next_id] = cy
                self.next_id += 1

        self.objects = updated_objects
        return self.objects, self.previous
