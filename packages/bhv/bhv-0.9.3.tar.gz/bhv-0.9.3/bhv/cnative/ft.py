from bhv.visualization import Image
from bhv.np import NumPyBoolBHV as BHV
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb



# Generate random Boolean sequences
num_sequences = 1024
sequence_length = 8192
np.random.seed(0)


def forward(data, transpose=False):
    freq = np.fft.fft(data, axis=not transpose)
    log_scale = np.log2(1 + np.abs(freq))
    return (255*log_scale/log_scale.max()).astype(np.uint8)

def complex_to_hsv(z, rmin, rmax, hue_start=90):
    amp = np.abs(z)
    amp = np.where(amp < rmin, rmin, amp)
    amp = np.where(amp > rmax, rmax, amp)
    ph = np.angle(z, deg=True) + hue_start
    # HSV are values in range [0,1]
    h = (ph % 360) / 360
    s = 0.85 * np.ones_like(h)
    v = (amp - rmin) / (rmax - rmin)
    return hsv_to_rgb(np.dstack((h, s, v)))

def forwardi(data):
    freq = np.fft.fft2(data)

    hsv = complex_to_hsv(freq, 0, 1)
    print(hsv.shape)
    plt.imsave('2d_gol1024.png', hsv, cmap="hsv")


def backward(data, transpose=False):
    log_scale = (data * np.log2(1 + np.abs(data.max())) / 255)
    freq_abs = 2**log_scale - 1
    # print(freq_abs.min(), freq_abs.max(), freq_abs.mean(), freq_abs.std())
    reconstructed = np.fft.ifft(freq_abs, axis=not transpose).real
    # print(reconstructed.min(), reconstructed.max(), reconstructed.mean(), reconstructed.std())
    return reconstructed > 0


def write_pgm(filename, np_array):
    """
    Write a NumPy array to a grayscale NetPBM (PGM) file.

    Parameters:
    - filename (str): The name of the file to save.
    - np_array (numpy.ndarray): 2D NumPy array of uint8 values representing grayscale image.
    """
    if np_array.dtype != np.uint8:
        raise ValueError("Input array must be of dtype uint8.")

    if len(np_array.shape) != 2:
        raise ValueError("Input array must be 2D.")

    height, width = np_array.shape
    maxval = 255  # For uint8

    # PGM Header
    header = f"P5\n{width} {height}\n{maxval}\n"

    with open(filename, 'wb') as f:
        f.write(header.encode())
        f.write(np_array.tobytes())


def load_pgm(filename):
    """
    Load a grayscale NetPBM (PGM) file into a NumPy array.

    Parameters:
    - filename (str): The name of the file to load.

    Returns:
    - np_array (numpy.ndarray): 2D NumPy array of uint8 values representing grayscale image.
    """
    with open(filename, 'rb') as f:
        # Read header
        header = f.readline().decode().strip()
        if header != 'P5':
            raise ValueError(f"Invalid PGM header: {header}")

        # Skip comments
        while True:
            line = f.readline().decode().strip()
            if not line.startswith("#"):
                break

        # Read image dimensions
        width, height = map(int, line.split())
        maxval = int(f.readline().decode().strip())

        if maxval != 255:
            raise ValueError(f"Unsupported max value: {maxval}")

        # Read image data and convert to NumPy array
        np_array = np.frombuffer(f.read(), dtype=np.uint8)
        np_array = np_array.reshape((height, width))

    return np_array


with open("gol1024.pbm", "rb") as f:
    boolean_sequences = np.array([list(hv.bits()) for hv in Image.load_pbm(f, BHV, True).hvs])
# write_pgm('ft_gol1024.pgm', forward(boolean_sequences, transpose=False))
# forwardi(boolean_sequences)

# boolean_sequences = backward(load_pgm("ft_gol.pgm"))
boolean_sequences = backward(boolean_sequences.astype(np.uint8)*255, transpose=True)
with open("ifT_gol1024.pbm", "wb") as f:
    Image([BHV(a) for a in boolean_sequences]).pbm(f, True)
