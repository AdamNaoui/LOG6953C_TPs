import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator
from qiskit.visualization import plot_histogram
import qiskit.quantum_info as qi

target = '01101'

# creating inversion about mean operator
A = [[1 / (2 ** len(target)) for i in range(2 ** len(target))] for j in range(2 ** len(target))]
# Convert to NumPy matrix
np_a = np.array(A)
I = np.identity(2 ** len(target))
matrix = -I + 2 * np_a

# Use Aer's qasm_simulator
simulator = QasmSimulator()
# Create quantum program that find 01101 by reversing its phase
x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
y = QuantumRegister(1, name='Y')
ands_results = QuantumRegister(9, name='ands_results')
res = ClassicalRegister(len(target), name='Target')

oracle = QuantumCircuit(x, y, ands_results, res, name='oracle')
oracle.h(x)

for j in range(int((2 ** len(target)) ** (1 / 2)) + 1):

    oracle.x(y)
    oracle.h(y)

    for i in range(len(target)):
        correct_index = len(target) - i - 1
        if target[i] == '0':
            oracle.x(x[correct_index], 'set to |1> for future CX gate')
            oracle.cx(x[correct_index], ands_results[correct_index])
            oracle.x(x[correct_index], 'undo')  # Reset x[i]
        else:
            oracle.cx(x[correct_index], ands_results[correct_index])

    # ands_results from 0 to 4 are all to |1> if x is 01101
    # We now have to apply ANDS gates to ands_results

    oracle.ccx(ands_results[0], ands_results[1], ands_results[5])
    oracle.ccx(ands_results[2], ands_results[3], ands_results[6])
    oracle.ccx(ands_results[5], ands_results[6],
               ands_results[7])  # ands_results[7] will be at |1> if x is 01101 or 01101

    oracle.ccx(ands_results[7], ands_results[4], ands_results[8])  # ands_results[8] will be at |1> if x is 01101

    # ands_results[8] contains f(x) value
    oracle.cx(ands_results[8], y)  # Apply CX gate to qubit ands_results[8], y in order to get f(x) output (classical
    # XOR)

    # Print the result
    inversion_about_mean = qi.Operator(matrix.tolist())
    oracle.unitary(inversion_about_mean, x, label='Inversion about mean')

# Map the quantum measurement to the classical bits
oracle.measure(x, res)

compiled_circuit = transpile(oracle, simulator)

# Execute the circuit on the qasm simulator
job = simulator.run(compiled_circuit, shots=10000)

# Grab results from the job
result = job.result()

# Returns counts
counts = result.get_counts(compiled_circuit)

# Draw the circuit
oracle.draw('mpl', filename='grover.png')

plot_histogram(counts, filename='grover_hist.png', title='Grover Histogram', bar_labels=True, figsize=(10, 8))
