class CentroidTracker:
    def __init__(self, max_distance=50):
        self.next_id = 0
        self.objects = {}
        self.previous = {}
        self.max_distance = max_distance

    def update(self, detections):
        new_objects = {}
        previous_positions = self.objects.copy()

        for cx, cy in detections:
            matched_id = None

            for object_id, (px, py) in self.objects.items():
                distance = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
                if distance < self.max_distance:
                    matched_id = object_id
                    break

            if matched_id is not None:
                new_objects[matched_id] = (cx, cy)
            else:
                new_objects[self.next_id] = (cx, cy)
                self.next_id += 1

        self.objects = new_objects
        return self.objects, previous_positions
