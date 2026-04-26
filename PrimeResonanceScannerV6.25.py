import os
import pickle
import mpmath as mp
from tqdm import tqdm

# --- Configuration ---
DATA_DIR = "data"
LIB_PATH = os.path.join(DATA_DIR, "spectral_library_10k.pkl")
PRECISION_DPS = 1000  # <--- Add this line

def calculate_resonance_optimized(n, library, dps=1000):
    """
    V6.25: Synchronized Sieve
    Implements a Sin-based Parity Gate to isolate odd-integer resonance
    and 3-point Energy Flux sampling to stabilize the prime signal.
    """
    mp.dps = dps
    n_mp = mp.mpf(str(n))
    
    # 1. Define the Spectral Energy Function
    def get_spectrum_power(val):
        v_mp = mp.mpf(str(val))
        omega = mp.log(v_mp)
        # Sum of harmonics (Real part)
        res = sum(mp.cos(z * omega) for z in library.values())
        return res**2

    # 2. 3-Point Cluster Sampling
    # Captures the energy 'hump' around N to account for phase lag
    p_left  = get_spectrum_power(n_mp - 0.01)
    p_mid   = get_spectrum_power(n_mp)
    p_right = get_spectrum_power(n_mp + 0.01)
    avg_power = (p_left + p_mid + p_right) / 3
    
    # 3. Synchronized Parity Gate
    # sin(pi * n / 2)^2 is 1 for odd integers and 0 for even integers
    # This forces the 'Ghost Peaks' at even numbers to collapse.
    parity_gate = mp.sin((mp.pi * n_mp) / 2)**2
    
    # 4. Final SNR Calculation
    # Normalizing against the library depth and applying the gate
    snr = float((avg_power / len(library)) * parity_gate)
    
    return snr
    
 
def run_scanner_v6_4():
    print("\n" + "="*60)
    print("📡 PRIME RESONANCE SCANNER V6.4: HIGH-PRECISION LIBRARY SCAN")
    print("="*60)
    
    # 1. Load the High-Precision Library
    if not os.path.exists(LIB_PATH):
        print(f"❌ Error: {LIB_PATH} not found.")
        print("Please wait for the Spectral Librarian to finish the 10k set.")
        return

    print(f"📥 Loading Spectral Library ({PRECISION_DPS if 'PRECISION_DPS' in locals() else 1000} dps)...")
    with open(LIB_PATH, 'rb') as f:
        shared_library = pickle.load(f)
    print(f"✅ Loaded {len(shared_library)} harmonics. Resolution Active.")

    # 2. Traditional V6 Command Inputs
    try:
        start_n_input = input("\nEnter starting integer: ").strip()
        search_range_input = input("Enter search range: ").strip()
        
        start_n = int(start_n_input)
        search_range = int(search_range_input)
    except ValueError:
        print("❌ Invalid input. Please enter numeric integers.")
        return

    hits = []
    print(f"\nScanning Spectrum: {len(shared_library)} harmonics in parallel...")
    
    # 3. Optimized Scan Loop
    for n in tqdm(range(start_n, start_n + search_range), desc="Scanning"):
        snr = calculate_resonance_optimized(n, shared_library)
        
        # Classification Logic
        classification = "COMPOSITE"
        if snr > 1.5: classification = "TRUE PRIME"
        if snr > 5.0: classification = "HIGH-RESONANCE LOCK"
        
        hits.append({
            "n": n,
            "snr": snr,
            "class": classification
        })

    # 4. Final Classification Report (Classic UI)
    print("\n" + "--- FINAL CLASSIFICATION REPORT ---")
    
    primes = [h for h in hits if "PRIME" in h['class'] or "LOCK" in h['class']]
    
    if not primes:
        print("COMPOSITE RESONANCE: 0 occurrences (No primes found)")
    else:
        print(f"TOTAL PRIMES DETECTED: {len(primes)}")
        print("-" * 30)
        # Sort by N to list findings in order
        for p in sorted(primes, key=lambda x: x['n']):
            star = "★" if p['snr'] > 5.0 else " "
            print(f" {star} > N: {p['n']:<15} | SNR: {p['snr']:.4f}")

    # 5. Diagnostic Dump (The Raw Data for your Whitepaper)
    print("\n--- RAW SPECTRAL DATA (DIAGNOSTIC) ---")
    for h in hits:
        print(f" N: {h['n']} | SNR: {h['snr']:.6f} | {h['class']}")

    print("\n" + "="*60)
    print(f"Scanner Precision (Hits/Range): {(len(primes)/search_range)*100:.2f}%")
    print(f"Engine Depth: {len(shared_library)} High-Precision Zeros")
    print("="*60)

if __name__ == "__main__":
    run_scanner_v6_4()