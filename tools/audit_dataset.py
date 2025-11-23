import json
from collections import Counter
import numpy as np

DATASET_FILE = "./data/viral_training/dataset.jsonl"

def audit_dataset():
    print(f"📊 AUDIT DEL DATASET: {DATASET_FILE}")
    
    try:
        with open(DATASET_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ File non trovato!")
        return

    total = len(lines)
    print(f"✅ Totale Esempi: {total}")

    styles = Counter()
    bpms = []
    valid_json = 0
    errors = 0

    for i, line in enumerate(lines):
        try:
            # 1. Decodifica la riga esterna
            entry = json.loads(line)
            
            # 2. Decodifica l'output (che è una stringa JSON interna)
            output_data = json.loads(entry['output'])
            
            # 3. Analisi Stile
            styles[output_data['style']] += 1
            
            # 4. Analisi BPM (Estraiamo dall'input stringa)
            # Format: [CONTEXT: ... | BPM: 120 | ...]
            input_str = entry['input']
            if "BPM:" in input_str:
                bpm_part = input_str.split("BPM:")[1].split("|")[0].strip()
                bpms.append(int(bpm_part))
            
            valid_json += 1
            
        except Exception as e:
            print(f"⚠️ Errore alla riga {i+1}: {e}")
            errors += 1

    print("\n--- 📈 STATISTICHE STILE ---")
    for style, count in styles.items():
        percent = (count / total) * 100
        print(f"- {style}: {count} ({percent:.1f}%)")

    print("\n--- 🎵 STATISTICHE AUDIO ---")
    if bpms:
        print(f"- BPM Medio: {int(np.mean(bpms))}")
        print(f"- BPM Minimo: {min(bpms)}")
        print(f"- BPM Massimo: {max(bpms)}")
        unique_bpms = len(set(bpms))
        print(f"- Varietà BPM: {unique_bpms} valori unici trovati")
        
        # Warning se sono tutti uguali
        if unique_bpms < 5:
            print("⚠️ ATTENZIONE: Poca varietà nei BPM. Il 'Bug 120' potrebbe aver colpito molti video.")
    else:
        print("❌ Nessun BPM rilevato nell'input.")

    print("\n--- 🏁 CONCLUSIONE ---")
    if errors == 0 and valid_json == total:
        print("🟢 Dataset INTEGRITÀ PERFETTA.")
    else:
        print(f"🔴 Trovati {errors} errori di formattazione.")

if __name__ == "__main__":
    audit_dataset()