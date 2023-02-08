import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator
from qiskit.visualization import plot_histogram

# Use Aer's qasm_simulator
simulator = QasmSimulator()
# Create quantum program that find 01101 by reversing its phase
x = QuantumRegister(5, name='X')  # 5 qubits index 0 is the right most qubit
y = QuantumRegister(1, name='Y')
ands_results = QuantumRegister(9, name='ands_results')
res = ClassicalRegister(1, name='res')
oracle = QuantumCircuit(x, y, ands_results, res, name='oracle')

oracle.x(y, 'init y with |1>')
# Apply Hadamard gate to X and Y
oracle.h(x)
oracle.h(y)

# Ensure each bit is correct in ands_results
oracle.cx(x[0], ands_results[0])  # ands_results[0] will be at |1> if x[0] is at |1>

oracle.x(x[1], 'set to |1> for future CX gate')
oracle.cx(x[1], ands_results[1])  # ands_results[1] will be at |1> if x[1] is at |0>
oracle.x(x[1], 'undo')  # Reset x[1]

oracle.cx(x[2], ands_results[2])  # ands_results[2] will be at |1> if x[2] is at |1>

oracle.cx(x[3], ands_results[3])  # ands_results[3] will be at |1> if x[3] is at |1>

oracle.x(x[4], 'set to |1> for future CX gate')
oracle.cx(x[4], ands_results[4])  # ands_results[4] will be at |1> if x[1] is at |0>
oracle.x(x[4], 'undo')  # Reset x[4]

# ands_results from 0 to 4 are all to |1> if x is 01101
# We now have to apply ANDS gates to ands_results

oracle.ccx(ands_results[0], ands_results[1], ands_results[5])
oracle.ccx(ands_results[2], ands_results[3], ands_results[6])
oracle.ccx(ands_results[5], ands_results[6], ands_results[7])  # ands_results[7] will be at |1> if x is 01101 or 01101

oracle.ccx(ands_results[7], ands_results[4], ands_results[8])  # ands_results[8] will be at |1> if x is 01101

# ands_results[8] contains f(x) value
oracle.cx(ands_results[8], y)  # Apply CX gate to qubit ands_results[8], y in order to get f(x) output (classical XOR)

# Map the quantum measurement to the classical bits
oracle.measure(ands_results[8], res)

compiled_circuit = transpile(oracle, simulator)

# Execute the circuit on the qasm simulator
job = simulator.run(compiled_circuit, shots=1000000)

# Grab results from the job
result = job.result()

# Returns counts
counts = result.get_counts(compiled_circuit)

# Draw the circuit
oracle.draw('mpl', filename='oracle.png')

plot_histogram(counts, filename='oracle_hist.png', title='Oracle Histogram', bar_labels=True)
