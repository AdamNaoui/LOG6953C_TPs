import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator
from qiskit.visualization import plot_histogram
import qiskit.quantum_info as qi
from oracle import oracle
from Z0 import Z0

target = '01101'
curr_oracle = oracle(target)
z0 = Z0(target)

# creating inversion about mean operator
A = [[1 / (2 ** len(target)) for i in range(2 ** len(target))] for j in range(2 ** len(target))]
# Convert to NumPy matrix
np_a = np.array(A)
I = np.identity(2 ** len(target))
matrix = -I + 2 * np_a

# Use Aer's qasm_simulator
simulator = QasmSimulator()
# Create quantum program that find 01101 by reversing its phase
x = QuantumRegister(len(target), name='x')  # 5 qubits index 0 is the right most qubit
ancilla = QuantumRegister(1, name='fx')
res = ClassicalRegister(len(target), name='Target')

grover = QuantumCircuit(x, res, ancilla, name='grover')
grover.h(x)
grover.barrier()
for j in range(int((2 ** len(target)) ** (1 / 2))):
    grover.reset(ancilla)
    grover.x(ancilla)
    grover.h(ancilla)  # init fx to |->
    grover.append(curr_oracle, x[:] + ancilla[:])
    grover.barrier()

    grover.reset(ancilla)
    grover.x(ancilla)
    grover.h(ancilla)  # init fx to |->

    grover.h(x)
    grover.append(z0, x[:] + ancilla[:])
    grover.h(x)
    grover.barrier()

# Map the quantum measurement to the classical bits
grover.measure(x, res)

compiled_circuit = transpile(grover, simulator)

# Execute the circuit on the qasm simulator
job = simulator.run(compiled_circuit, shots=100000)

# Grab results from the job
result = job.result()

# Returns counts
counts = result.get_counts(compiled_circuit)

# Draw the circuit
grover.draw('mpl', filename='grover.png')

plot_histogram(counts, filename='grover_hist.png', title='Grover Histogram', bar_labels=True, figsize=(10, 8))
