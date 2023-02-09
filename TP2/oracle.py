import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator
from qiskit.visualization import plot_histogram
import qiskit.quantum_info as qi

target = '01101'  # len(target) must be >= 2
# Use Aer's qasm_simulator
simulator = QasmSimulator()
# Create quantum program that find 01101 by reversing its phase
x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
y = QuantumRegister(1, name='Y')
ands_results = QuantumRegister(len(target) - 1, name='ands_results')
res = ClassicalRegister(1, name='res')

oracle = QuantumCircuit(x, y, ands_results, res, name='oracle')

oracle.x(y, 'init y with |1>')

# Apply Hadamard gate to X and Y
oracle.h(x)
oracle.h(y)

for i in range(len(target) - 1):
    correct_index = len(target) - i - 1
    if i == 0:
        if target[correct_index] == '0':
            oracle.x(x[i], 'correct bit is 0, set to |1> for future CCX gate')
        if target[correct_index - 1] == '0':
            oracle.x(x[i + 1],'correct bit is 0, set to |1> for future CCX gate')

        oracle.ccx(x[i], x[i + 1], ands_results[i])

        if target[correct_index] == '0':
            oracle.x(x[i], 'undo setter')
        if target[correct_index - 1] == '0':
            oracle.x(x[i + 1], 'undo setter')

        continue

    if target[correct_index - 1] == '0':
        oracle.x(x[i + 1], 'correct bit is 0, set to |1> for future CCX gate')

    oracle.ccx(ands_results[i - 1], x[i + 1], ands_results[i])

    if target[correct_index - 1] == '0':
        oracle.x(x[i + 1], 'undo setter')

# ands_results[len(target) - 2] contains f(x) value
# Apply CX gate to qubit ands_results[8], y in order to get f(x) output (classical XOR)
oracle.cx(ands_results[len(target) - 2], y)

# Map the quantum measurement to the classical bits
oracle.measure(ands_results[len(target) - 2], res)

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
