import subprocess
import threading

class RecorderThread(threading.Thread):
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename
        self.process = None

    def run(self):
        command = ['arecord', '-f', 'cd', '-t', 'wav', self.filename]
        self.process = subprocess.Popen(command)
        self.process.wait()

    def stop(self):
        self.process.terminate()

if __name__ == '__main__':
    # Start the recorder thread
    recorder = RecorderThread('recording.wav')
    recorder.start()

    # Wait for user input to stop recording
    input('Press Enter to stop recording...')

    # Stop the recorder thread
    recorder.stop()