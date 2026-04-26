import os
import pickle
from mpmath import mp
from tqdm import tqdm

# --- CONFIGURATION ---
TARGET_ZEROS = 50000
PRECISION_DPS = 1000  # Matching your Test 3 requirements
DB_PATH = "data/spectral_library_10k.pkl"
os.makedirs("data", exist_ok=True)

def build_spectral_library():
    mp.dps = PRECISION_DPS
    
    # Check for existing partial library to resume
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'rb') as f:
            library = pickle.load(f)
        print(f"📡 Found existing library with {len(library)} zeros. Resuming...")
    else:
        library = {}
        print(f"📡 Initializing new High-Precision Library ({PRECISION_DPS} dps)...")

    start_index = len(library) + 1
    
    try:
        for i in tqdm(range(start_index, TARGET_ZEROS + 1), desc="Building Library"):
            # Calculate the imaginary part of the i-th zero
            # This is the "Nuclear" calculation
            z = mp.zetazero(i).imag
            
            # Store as a high-precision mpf object
            library[i] = z
            
            # Auto-save every 100 zeros to prevent data loss
            if i % 100 == 0:
                with open(DB_PATH, 'wb') as f:
                    pickle.dump(library, f)
                    
    except KeyboardInterrupt:
        print("\n⚠️ Build paused by user. Saving progress...")
    finally:
        with open(DB_PATH, 'wb') as f:
            pickle.dump(library, f)
        print(f"\n✅ Library Sync Complete: {len(library)} zeros stored in {DB_PATH}")

if __name__ == "__main__":
    build_spectral_library()
