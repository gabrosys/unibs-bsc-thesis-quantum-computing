# Bachelor's Thesis: Quantum Computing

- **Author:** Gabriele Rossini
- **Degree:** B.Sc. in Software Engineering / Computer Engineering
- **University:** Università degli studi di Brescia

## Quantum Algorithm Development: From Circuit Model to Qiskit

- [Full Thesis (PDF)](it-thesis-qc.pdf). _(The document is written in Italian)._

## Setup

This guide provides step-by-step instructions to set up a local development environment for this project.

### Virtual Environment

Using a virtual environment is a best practice to manage project dependencies and avoid conflicts.

**Create the virtual environment:**

```bash
python3 -m venv .venv
```

**Activate the virtual environment:**

```bash
source .venv/bin/activate
```

### Install Dependencies

Now, install the required Python packages using `pip`.

**Upgrade Pip**
Ensure you have the latest version of the package installer.

```bash
pip install --upgrade pip
```

**Install from `requirements.txt`**
Install all the project dependencies using the provided file.

```bash
pip install -r requirements.txt
```

## Execute

The main application logic is in `main.py`. It runs Grover's algorithm based on the settings defined in `config.json`.

### 1. Configure the Simulation

Open the `config.json` file to adjust the parameters for the execution.

```json
{
  "n_qubits": 3,
  "target_state": "101",
  "shots": 1024,
  "use_real_hardware": false,
  "output_filename": "output.png"
}
```

- `n_qubits`: The number of qubits in the quantum register.
- `target_state`: The binary string to search for. Its length must match `n_qubits`.
- `shots`: The number of times to run the circuit to gather statistics.
- `use_real_hardware`: Set to `false` for local simulation or `true` to run on IBM Quantum hardware.
- `output_filename`: The name of the file where the results histogram will be saved.

### 2. Running the Application

#### A. Local Simulation

To run the algorithm on your local machine using the Aer simulator, ensure `"use_real_hardware"` is set to `false` in `config.json`.

Then, execute the main script from your terminal:

```bash
python3 main.py
```

The script will print the circuit diagram, execution results, and save a histogram image (`output.png` by default).

#### B. Real Quantum Hardware

To execute the algorithm on a real IBM Quantum computer, follow these steps:

**1. Set up IBM Quantum Account**

You need an API token from IBM Quantum.

- Go to the [IBM Quantum Platform](https://quantum.ibm.com/) and create a free account.
- Find your API token on your account page.

Save your credentials locally. The script will automatically use them. Replace `"YOUR_IBM_QUANTUM_TOKEN"` with your actual token.

```python
# Run this once in a Python shell or a separate script
python3 -c "from qiskit_ibm_runtime import QiskitRuntimeService; QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_IBM_QUANTUM_TOKEN', overwrite=True)"
```

**2. Configure for Hardware Execution**

In `config.json`, change `"use_real_hardware"` to `true`:

```json
// filepath: config.json
// ...existing code...
  "shots": 1024,
  "use_real_hardware": true,
  "output_filename": "output.png"
}
```

**3. Run the Script**

Execute the main script. It will connect to IBM Quantum, find the least busy backend that meets the qubit requirement, and submit the job.

```bash
python3 main.py
```

> **Note:** Jobs on real hardware are queued and may take some time to complete. The script will wait for the results before finishing.
