import json
import threading
import time

class JsonDict(dict):
    def __init__(self, path):
        super().__init__()
        self.path = path
        with open(path, 'r') as f:
            self.update(json.load(f))
        self._running = True
        self.save_thread = threading.Thread(target=self._save_thread)
        self.save_thread.start()

    def _save_thread(self):
        while self._running:
            self.save()
            time.sleep(5)

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self, f, indent=4)

    def reload(self):
        self.save()
        with open(self.path, 'r') as f:
            self.clear()
            self.update(json.load(f))

    def close(self):
        self._running = False
        self.save_thread.join()

class JsonList(list):
    def __init__(self, path):
        super().__init__()
        self.path = path
        with open(path, 'r') as f:
            self.extend(json.load(f))
        self._running = True
        self.save_thread = threading.Thread(target=self._save_thread)
        self.save_thread.start()

    def _save_thread(self):
        while self._running:
            self.save()
            time.sleep(5)

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self, f, indent=4)

    def reload(self):
        self.save()
        with open(self.path, 'r') as f:
            self.clear()
            self.extend(json.load(f))

    def close(self):
        self._running = False
        self.save_thread.join()