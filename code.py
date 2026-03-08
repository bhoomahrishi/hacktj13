import numpy as np
import time
import hashlib
from video import Video


class PhotonSensor:

    def __init__(self):
        self.camera = Video()

    def read_photon_packet(self):

        photons = self.camera.get_quantum_bits()
        timestamp = time.time()

        return photons, timestamp


class ShotNoiseDetector:

    def __init__(self, window_size=50):

        self.window_size = window_size
        self.measurements = []

    def add_measurement(self, photons):

        self.measurements.append(photons)

        if len(self.measurements) > self.window_size:
            self.measurements.pop(0)

    def detect_shot_noise(self):

        if len(self.measurements) < self.window_size:
            return False

        mean = np.mean(self.measurements)
        variance = np.var(self.measurements)

        ratio = variance / mean if mean > 0 else 0

        return 0.8 < ratio < 1.2


class QuantumRNG:

    def __init__(self):

        self.random_bits = ""

    def extract_entropy(self, photon_count, timestamp):

        data = f"{photon_count}-{timestamp}".encode()

        digest = hashlib.sha256(data).digest()

        bits = ''.join(f'{byte:08b}' for byte in digest)

        self.random_bits += bits

        # prevent memory explosion
        if len(self.random_bits) > 10000:
            self.random_bits = self.random_bits[-5000:]

    def get_random_bits(self, bit_length):

        if len(self.random_bits) < bit_length:
            return None

        bits = self.random_bits[:bit_length]
        self.random_bits = self.random_bits[bit_length:]

        return bits

    def get_random_number(self, bit_length=32):

        bits = self.get_random_bits(bit_length)

        if bits is None:
            return None

        return int(bits, 2)


class CryptoKeyGenerator:

    def __init__(self, qrng):

        self.qrng = qrng

    def generate_key(self, bit_length=256):

        bits = self.qrng.get_random_bits(bit_length)

        if bits is None:
            return None

        return hex(int(bits,2))[2:].zfill(bit_length//4)


class ShotNoiseAlert:

    def notify(self):
        print("Shot Noise Detected — Quantum Randomness Active")


class QuantumShotNoiseSystem:

    def __init__(self):

        self.sensor = PhotonSensor()
        self.detector = ShotNoiseDetector()
        self.qrng = QuantumRNG()
        self.alert = ShotNoiseAlert()

        self.keygen = CryptoKeyGenerator(self.qrng)