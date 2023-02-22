from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator


def Z0(target):
    # Create quantum program that find 01101 by reversing its phase
    x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
    ancilla = QuantumRegister(1, name='fx')  # has to be init to |->
    z0 = QuantumCircuit(x, ancilla, name='Z0')

    # set x qubits so that the target will control the gate
    for i in range(len(target)):
        z0.x(x[i])

    z0.mct(x[:], ancilla)  # automatically we get a kickback if |0> cause ancilla was in |->
    z0.z(ancilla)  # switch phase to all qubits in the superposition

    # reset x qubits to their original state
    for i in range(len(target)):
        z0.x(x[i])

    z0.to_gate()

    return z0
