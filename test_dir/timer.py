import time
class Timer:
    def __init__(self, name='function') -> None:
        self.name = name
        pass
    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        print(f"Elapsed time of {self.name}: {elapsed_time:.6f} seconds")