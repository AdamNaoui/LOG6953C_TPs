import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister, execute, IBMQ

from qiskit_aer import QasmSimulator
from qiskit.visualization import plot_histogram
import qiskit.quantum_info as qi
IBMQ.save_account('e31a3c8ff39a7a22b6a3052adfb2d4d150b53f5bcac9b161fefba1349302c57ffbf55da2b310ecd734c74be5874804be20d4c1cc4e0345e74db6569e9989fab8', overwrite=True)
provider = IBMQ.load_account()
backend = provider.backends.simulator_statevector

target = '01101'

# creating inversion about mean operator
A = [[1 / (2 ** len(target)) for i in range(2 ** len(target))] for j in range(2 ** len(target))]
# Convert to NumPy matrix
np_a = np.array(A)
I = np.identity(2 ** len(target))
matrix = -I + 2 * np_a

# Use Aer's qasm_simulator
# simulator = QasmSimulator()
# Create quantum program that find 01101 by reversing its phase
x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
y = QuantumRegister(1, name='Y')
ands_results = QuantumRegister(len(target) - 1, name='ands_results')
res = ClassicalRegister(len(target), name='Target')

grover = QuantumCircuit(x, y, ands_results, res, name='grover')
grover.h(x)

for j in range(int((2 ** len(target)) ** (1 / 2))):
    grover.reset(y)
    grover.x(y, 'init y with |1>')
    grover.h(y)
    for i in range(len(target) - 1):
        correct_index = len(target) - i - 1
        if i == 0:
            if target[correct_index] == '0':
                grover.x(x[i], 'correct bit is 0, set to |1> for future CCX gate')
            if target[correct_index - 1] == '0':
                grover.x(x[i + 1], 'correct bit is 0, set to |1> for future CCX gate')

            grover.ccx(x[i], x[i + 1], ands_results[i])

            if target[correct_index] == '0':
                grover.x(x[i], 'undo setter')
            if target[correct_index - 1] == '0':
                grover.x(x[i + 1], 'undo setter')

            continue

        if target[correct_index - 1] == '0':
            grover.x(x[i + 1], 'correct bit is 0, set to |1> for future CCX gate')

        grover.ccx(ands_results[i - 1], x[i + 1], ands_results[i])

        if target[correct_index - 1] == '0':
            grover.x(x[i + 1], 'undo setter')

    # ands_results[len(target) - 2] contains f(x) value
    # Apply CX gate to qubit ands_results[8], y in order to get f(x) output (classical XOR)
    grover.cx(ands_results[len(target) - 2], y)

    inversion_about_mean = qi.Operator(matrix.tolist())
    grover.unitary(inversion_about_mean, x, label='Inversion about mean')
    grover.x(ands_results)

# Map the quantum measurement to the classical bits
grover.measure(x, res)

# compiled_circuit = transpile(grover, simulator)
transpiled = transpile(grover, backend=backend)
job = backend.run(transpiled, shots=20000)
# Execute the circuit on the qasm simulator

# Grab results from the job
result = job.result()

# Returns counts
counts = result.get_counts(grover)

# Draw the circuit
grover.draw('mpl', filename='grover_ibmq.png')

plot_histogram(counts, filename='grover_ibmq_hist.png', title='Grover IBMQ Histogram', bar_labels=True, figsize=(10, 8))
