from qiskit import QuantumCircuit

class GroverAlgorithm:
    def __init__(self, n_qubits, target_state):
        """
        Initializes the Grover Algorithm builder.
        
        :param n_qubits: Dimension of the register (n).
        :param target_state: Binary string representing the winner state 'w' (e.g., '101').
        """
        self.n = n_qubits
        self.target = target_state
        
        # Validation: Ensure target length matches the number of qubits
        if len(target_state) != n_qubits:
            raise ValueError("Target state length must match n_qubits.")

    def create_oracle(self):
        """
        Constructs the Phase Oracle (Z_f).
        
        It inverts the phase only for the target state |w>.
        Transformation: |x> -> (-1)^f(x) |x>
        """
        qc = QuantumCircuit(self.n)
        
        # 1. Apply X gates to qubits that are '0' in the target string.
        #    This 'wraps' the state so the control activates only on |11...1>.
        #    Note: Qiskit uses little-endian ordering (qubit 0 is the rightmost bit).
        for i, bit in enumerate(reversed(self.target)):
            if bit == '0':
                qc.x(i)
        
        # 2. Apply a Multi-Controlled Z gate (MCZ).
        #    Since Qiskit may not have a direct MCZ for all backends, we construct it
        #    using a Multi-Controlled X (MCX) sandwiched between Hadamard gates 
        #    on the target qubit (last qubit).
        qc.h(self.n - 1)
        qc.mcx(list(range(self.n - 1)), self.n - 1)
        qc.h(self.n - 1)
        
        # 3. Uncomputation (Reverse the X gates).
        #    This returns the qubits to their original state, leaving only the phase flipped.
        for i, bit in enumerate(reversed(self.target)):
            if bit == '0':
                qc.x(i)
                
        # Convert to a gate instruction for a cleaner circuit diagram
        oracle_gate = qc.to_instruction()
        oracle_gate.name = "Oracle (Z_f)"
        return oracle_gate

    def create_diffuser(self):
        """
        Constructs the Diffuser Operator (Grover's Diffusion Operator).
        
        D = H^n * Z_OR * H^n = 2|u><u| - I
        This operator performs the inversion about the mean.
        """
        qc = QuantumCircuit(self.n)
        
        # 1. Apply Hadamard gates to all qubits to transform the basis.
        qc.h(range(self.n))
        
        # 2. Apply X gates to all qubits.
        qc.x(range(self.n))
        
        # 3. Apply Multi-Controlled Z (MCZ) to perform reflection about |0...0>.
        qc.h(self.n - 1)
        qc.mcx(list(range(self.n - 1)), self.n - 1)
        qc.h(self.n - 1)
        
        # 4. Uncompute X and H gates (Inverse transformation).
        qc.x(range(self.n))
        qc.h(range(self.n))
        
        diffuser_gate = qc.to_instruction()
        diffuser_gate.name = "Diffuser (D)"
        return diffuser_gate

    def build_circuit(self, iterations):
        """
        Assembles the complete Grover circuit.
        
        Sequence:
        1. Initialization (Superposition)
        2. Grover Iterations (G = D * Z_f)
        3. Measurement
        """
        qc = QuantumCircuit(self.n, self.n)
        
        # Phase 1: Initialization
        # Create a uniform superposition |u>
        qc.h(range(self.n))
        
        # Create the operators
        oracle = self.create_oracle()
        diffuser = self.create_diffuser()
        
        # Phase 2: Grover Loop
        for _ in range(iterations):
            qc.append(oracle, range(self.n))
            qc.append(diffuser, range(self.n))
            
        # Phase 3: Measurement
        qc.measure(range(self.n), range(self.n))
        
        return qc