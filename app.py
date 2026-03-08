import streamlit as st
import numpy as np
import time
from code import QuantumShotNoiseSystem

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="QuantumRNG Dashboard", layout="wide")

st.title("🌌 Quantum Shot-Noise Entropy Engine")
st.markdown("Real-time Quantum Random Number Generator using camera shot noise.")

# ---------------- SIDEBAR ----------------
st.sidebar.header("System Settings")

run_system = st.sidebar.toggle("Start Quantum Acquisition")

bit_length = st.sidebar.selectbox(
    "Key Length",
    [128, 256, 512],
    index=1
)

refresh_rate = st.sidebar.slider(
    "Refresh Rate (ms)",
    10,
    500,
    50
)

# ---------------- SESSION STATE ----------------
if "photon_history" not in st.session_state:
    st.session_state.photon_history = []

# ---------------- BACKEND INIT ----------------
@st.cache_resource
def get_system():
    return QuantumShotNoiseSystem()

system = get_system()

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Quantum Variance Monitor")
    chart = st.empty()

with col2:
    st.subheader("Live Metrics")

    fano_metric = st.empty()
    photon_metric = st.empty()

    st.subheader("Generated Quantum Key")
    key_box = st.empty()

st.markdown("---")

st.subheader("Entropy Bitstream")
bitstream = st.empty()

# ---------------- MAIN LOOP ----------------
if run_system:

    photons, timestamp = system.sensor.read_photon_packet()

    # Update detector
    system.detector.add_measurement(photons)

    # Extract entropy
    system.qrng.extract_entropy(photons, timestamp)

    # Calculate Fano factor
    measurements = system.detector.measurements

    if len(measurements) > 1:
        mean_val = np.mean(measurements)
        var_val = np.var(measurements)
        fano = var_val / mean_val if mean_val > 0 else 0
    else:
        fano = 0

    st.session_state.photon_history.append(photons)

    if len(st.session_state.photon_history) > 100:
        st.session_state.photon_history.pop(0)

    # ---------------- UI UPDATES ----------------

    fano_metric.metric(
        "Fano Factor",
        f"{fano:.4f}"
    )

    photon_metric.metric(
        "Photon Noise Metric",
        f"{photons:.2f}"
    )

    bits = system.qrng.random_bits[-256:]
    bitstream.code(bits if bits else "Collecting entropy...")

    # Key generation
    key = system.keygen.generate_key(bit_length)

    if key:
        key_box.code(key)
    else:
        key_box.info("Collecting entropy...")

    # Chart
    chart.line_chart(st.session_state.photon_history)

    # Streamlit refresh
    time.sleep(refresh_rate / 1000)
    st.rerun()

else:
    st.warning("Enable **Start Quantum Acquisition** in the sidebar.")