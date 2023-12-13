import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sampling rate in Hz
INTERVAL = 30  # Update interval in milliseconds

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize plot
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))

# Function to update the plot
def update_plot(frame):
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    line.set_ydata(data)
    return line,

# Set up the animation
ani = FuncAnimation(fig, update_plot, blit=True)

# Show the plot (non-blocking)
plt.show(block=False)

try:
    # Start the animation
    plt.pause(0.01)
    while True:
        pass
except KeyboardInterrupt:
    # Stop the stream and close the PyAudio instance
    stream.stop_stream()
    stream.close()
    p.terminate()
    plt.close()