from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator


def oracle(target):
    # Create quantum program that find 01101 by reversing its phase
    x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
    ancilla = QuantumRegister(1, name='fx')  # has to be init to |->
    oracle_circuit = QuantumCircuit(x, ancilla, name='oracle')

    # set x qubits so that the target will control the gate
    for i in range(len(target)):
        correct_index = len(target) - i - 1
        if target[correct_index] == '0':
            oracle_circuit.x(x[i])

    oracle_circuit.mct(x[:], ancilla)  # automatically we get a kickback cause ancilla was in |->

    # reset x qubits to their original state
    for i in range(len(target)):
        correct_index = len(target) - i - 1
        if target[correct_index] == '0':
            oracle_circuit.x(x[i])

    oracle_circuit.to_gate()

    return oracle_circuit
