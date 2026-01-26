import sys
import os
import math
import json
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())

from src.logic import GroverAlgorithm
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as IBMSampler
from qiskit import transpile

def save_histogram(counts, target_state, filename):
    sorted_keys = sorted(counts.keys())
    sorted_values = [counts[k] for k in sorted_keys]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(sorted_keys, sorted_values, color='#648fff', edgecolor='black')
    
    if target_state in sorted_keys:
        index = sorted_keys.index(target_state)
        bars[index].set_color('#dc267f')
        bars[index].set_edgecolor('black')

    plt.xlabel('Computational Basis States')
    plt.ylabel('Counts')
    plt.title(f"Grover's Algorithm Results (Target: |{target_state}>)")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{int(height)}',
                 ha='center', va='bottom')

    plt.savefig(filename, dpi=300)
    print(f"> Histogram saved successfully: {filename}")
    plt.close()

def load_configuration(file_name="config.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Configuration file not found at: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[ERROR] File '{file_path}' is not valid JSON.")
        sys.exit(1)

def calculate_optimal_iterations(n_qubits, n_solutions=1):
    N = 2**n_qubits
    theta = math.asin(math.sqrt(n_solutions / N))
    return round((math.pi / (4 * theta)) - 0.5)

def get_backend(use_real_hardware, n_qubits):
    if use_real_hardware:
        print("> Connecting to IBM Quantum Service...")
        try:
            service = QiskitRuntimeService()
            print("> Searching for least busy quantum backend...")
            backend = service.least_busy(operational=True, simulator=False, min_num_qubits=n_qubits)
            print(f"> Selected Backend: {backend.name} (Real Hardware)")
            return backend
        except Exception as e:
            print(f"[ERROR] Failed to connect to IBM Quantum: {e}")
            sys.exit(1)
    else:
        print("> Using Local Aer Simulator")
        return AerSimulator()

def extract_counts_from_result(job_result, use_real_hw):
    if not use_real_hw:
        return job_result.get_counts()
    
    try:
        pub_result = job_result[0]
        data = pub_result.data
        if hasattr(data, 'c'):
            return data.c.get_counts()
        elif hasattr(data, 'meas'):
            return data.meas.get_counts()
        else:
            first_field = list(data.keys())[0]
            return getattr(data, first_field).get_counts()
    except Exception as e:
        print(f"[ERROR] Failed to extract counts from V2 result: {e}")
        sys.exit(1)

def main():
    print("=== Grover's Algorithm Simulation ===")

    config = load_configuration()
    
    n_qubits = config["n_qubits"]
    target = config["target_state"]
    shots = config["shots"]
    output_file = config.get("output_filename", "histogram.png")
    use_real_hw = config.get("use_real_hardware", False)

    if len(target) != n_qubits:
        print(f"[ERROR] Target length '{len(target)}' does not match n_qubits '{n_qubits}'")
        sys.exit(1)

    print("Configuration Loaded:")
    print(f"  - Qubits: {n_qubits}")
    print(f"  - Target: |{target}>")
    print(f"  - Shots:  {shots}")
    print(f"  - Mode:   {'Real Hardware' if use_real_hw else 'Local Simulation'}")
    
    t_opt = calculate_optimal_iterations(n_qubits)
    print(f"\n> Optimal iterations calculated: {t_opt}")
    
    grover = GroverAlgorithm(n_qubits, target)
    qc = grover.build_circuit(iterations=t_opt)

    print("\n=== Abstract Circuit Diagram ===")
    print(qc.draw(output='text'))
    
    backend = get_backend(use_real_hw, n_qubits)
    
    print(f"\n> Transpiling circuit for {backend.name}...")
    transpiled_qc = transpile(qc, backend, optimization_level=3)
    
    print(f"  - Depth: {transpiled_qc.depth()}")
    print(f"  - Gate Count: {transpiled_qc.count_ops()}")
    
    print(f"\n> Executing job with {shots} shots...")
    
    if use_real_hw:
        sampler = IBMSampler(mode=backend)
        job = sampler.run([transpiled_qc], shots=shots)
    else:
        job = backend.run(transpiled_qc, shots=shots)
        
    result = job.result()
    counts = extract_counts_from_result(result, use_real_hw)
    
    print("\n=== Experimental Results ===")
    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
    print(sorted_counts)

    save_histogram(counts, target, output_file)
    
    success_count = counts.get(target, 0)
    success_rate = (success_count / shots) * 100
    
    print(f"\n> Target state |{target}> found in {success_rate:.2f}% of shots.")
    
    top_result = list(sorted_counts.keys())[0]
    if top_result == target:
        print("\n[OUTCOME] SUCCESS: Probability peak matches target.")
    else:
        print("\n[OUTCOME] FAILURE: Target is not the most frequent result.")

if __name__ == "__main__":
    main()