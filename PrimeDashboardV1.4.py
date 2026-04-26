import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mpmath import mp
import pickle
import os

# --- CORE V6.25 ANALYTICS ENGINE ---
def calculate_resonance_v625(n, library, dps=1000):
    mp.dps = dps
    n_mp = mp.mpf(str(n))
    
    def get_spectrum_power(val):
        v_mp = mp.mpf(str(val))
        omega = mp.log(v_mp)
        res = sum(mp.cos(z * omega) for z in library.values())
        return res**2

    p_mid   = get_spectrum_power(n_mp)
    p_left  = get_spectrum_power(n_mp - 0.01)
    p_right = get_spectrum_power(n_mp + 0.01)
    avg_power = (p_left + p_mid + p_right) / 3
    
    parity_gate = mp.sin((mp.pi * n_mp) / 2)**2
    snr = float((avg_power / len(library)) * parity_gate)
    return snr

# --- UI CONFIGURATION ---
st.set_page_config(page_title="PRS Dashboard V1.4", layout="wide")
st.title("📡 Prime Resonance Scanner | V1.4 Singularity Shield")

# --- DATA PERSISTENCE ---
@st.cache_resource
def load_spectral_library():
    path = "data/spectral_library_10k.pkl"
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
    return None

if 'saved_pattern' not in st.session_state:
    st.session_state.saved_pattern = None

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Scanner Configuration")
st.sidebar.success("Hardware: Multi-Core Harmonic Array")

start_n = st.sidebar.text_input("Starting Integer (N)", value="1")
scan_len = st.sidebar.slider("Scan Range", 1, 100, 20)
threshold = st.sidebar.slider("Detection Threshold (SNR)", 0.0, 10.0, 1.0)

st.sidebar.markdown("---")
st.sidebar.header("Visualization Settings")
# Toggle for Logarithmic Scale to see small details
use_log = st.sidebar.checkbox("Apply Logarithmic Scaling (dB)", value=False)

# --- EXECUTION ENGINE ---
library = load_spectral_library()

if library is None:
    st.error("❌ Primary library (spectral_library_10k.pkl) not found.")
else:
    if st.sidebar.button("Execute Harmonic Scan"):
        results = []
        p_bar = st.progress(0)
        p_text = st.empty()
        
        for i, n in enumerate(range(int(start_n), int(start_n) + scan_len)):
            p_text.text(f"Synchronizing Coordinate N: {n}...")
            
            # --- THE SINGULARITY SHIELD ---
            # We bypass N=1 to prevent the 'Unity Spike' from washing out the primes
            if n == 1:
                snr_val = 0.0 
            else:
                snr_val = calculate_resonance_v625(n, library)
                
            status = "PRIME" if snr_val >= threshold else "COMPOSITE"
            results.append({"N": n, "SNR": snr_val, "Type": status})
            p_bar.progress((i + 1) / scan_len)
        
        p_bar.empty()
        p_text.empty()
        st.session_state.current_df = pd.DataFrame(results)

    # --- UI RENDER BLOCK ---
    if 'current_df' in st.session_state:
        df = st.session_state.current_df
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Resonance Field Visualization")
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.set_facecolor('#0E1117')
            fig.patch.set_facecolor('#0E1117')
            
            display_snr = df['SNR']
            # Apply Log Scale if selected
            if use_log:
                display_snr = np.log10(df['SNR'] + 1e-6) # Add epsilon to avoid log(0)
                ax.set_ylabel("Log SNR (Magnitude)", color='white')
            else:
                ax.set_ylabel("Linear SNR", color='white')

            # Reference Pattern Plotting
            if st.session_state.saved_pattern is not None:
                saved_snr = st.session_state.saved_pattern['SNR']
                if use_log: saved_snr = np.log10(saved_snr + 1e-6)
                ax.plot(range(len(df)), saved_snr, color='#00D4FF', 
                        linestyle='--', linewidth=2, label="Reference Pattern", zorder=3)

            # Active Scan Plotting
            colors = ['#00FF41' if t == "PRIME" else '#FF3131' for t in df['Type']]
            ax.bar(range(len(df)), display_snr, color=colors, alpha=0.8, label="Active Scan")
            
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(df['N'], rotation=45, color='white')
            ax.tick_params(colors='white')
            ax.legend()
            st.pyplot(fig)

        with col2:
            st.subheader("Action Center")
            if st.button("💾 Save as Reference"):
                st.session_state.saved_pattern = df
                st.toast("Pattern locked!")
            
            if st.button("🗑️ Clear Reference"):
                st.session_state.saved_pattern = None
                st.rerun()

            st.dataframe(df, use_container_width=True)
            
            if st.session_state.saved_pattern is not None and len(df) == len(st.session_state.saved_pattern):
                corr = df['SNR'].corr(st.session_state.saved_pattern['SNR'])
                st.metric("Coherence Score", f"{max(0, corr*100):.2f}%")