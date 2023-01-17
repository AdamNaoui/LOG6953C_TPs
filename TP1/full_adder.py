import numpy as np
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister

from qiskit.visualization import plot_histogram
from qiskit_aer import QasmSimulator

# Use Aer's qasm_simulator
simulator = QasmSimulator()
inputs = QuantumRegister(3, name='inputs')
consts_zeros = QuantumRegister(4, name='consts_0')
sum_carry_res = ClassicalRegister(2, name='sum_carry')
q = QuantumRegister(2, name='temps')
sum_res = QuantumRegister(1, name='sum')
carry_res = QuantumRegister(1, name='carry')

# Create a Quantum Circuit acting on the q register
circuit = QuantumCircuit(inputs, sum_carry_res, q, sum_res, consts_zeros,carry_res)

circuit.h(inputs)  # Apply Hadamard gate to qubits

# make all AND permutation of couple from ABC
circuit.ccx(inputs[0], inputs[1], consts_zeros[0])
circuit.ccx(inputs[0], inputs[2], consts_zeros[1])
circuit.ccx(inputs[1], inputs[2], consts_zeros[2])

# carry equals the or between all the consts_ones
circuit.x(consts_zeros[0])
circuit.x(consts_zeros[1])
circuit.ccx(consts_zeros[0], consts_zeros[1], consts_zeros[3])
# circuit.x(consts_zeros[3]) not necessary cause with have to cancel it for the next OR
circuit.x(consts_zeros[2])
circuit.ccx(consts_zeros[3], consts_zeros[2], carry_res[0])
circuit.x(carry_res[0])

circuit.cx(inputs[1], inputs[2])  # Apply CX gate to qubit B and C

circuit.x(inputs[0])  # reverse A to compute q1

circuit.ccx(inputs[0], inputs[2], q[0])

circuit.x(inputs[0])  # cancel previous reverse to compute q2

circuit.x(inputs[2])  # reverse A to compute q2

circuit.ccx(inputs[0], inputs[2], q[1])

circuit.x(sum_res[0])  # init sum with 1 to compute sum
circuit.x(q[0])  # reverse q0 to compute sum
circuit.x(q[1])  # reverse q1 to compute sum
circuit.ccx(q[0], q[1], sum_res[0])

circuit.measure([sum_res[0], carry_res[0]], [sum_carry_res[0], sum_carry_res[1]])
compiled_circuit = transpile(circuit, simulator)

# Execute the circuit on the qasm simulator
job = simulator.run(compiled_circuit, shots=100000)

# Grab results from the job
result = job.result()

# Returns counts
counts = result.get_counts(compiled_circuit)

# Draw the circuit
circuit.draw('mpl', filename='full_adder_circuit.png')

plot_histogram(counts, filename='full_adder_histogram.png', title='Full Adder Histogram', bar_labels=True)
