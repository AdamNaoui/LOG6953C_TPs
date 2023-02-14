from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator


def oracle(target):
    # Create quantum program that find 01101 by reversing its phase
    x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
    fx = QuantumRegister(1, name='fx')
    oracle_circuit = QuantumCircuit(x, fx, name='oracle')

    for i in range(len(target)):
        correct_index = len(target) - i - 1
        if target[correct_index] == '0':
            oracle_circuit.x(x[i])

    oracle_circuit.mct(x[:], fx)

    oracle_circuit.cz(fx, x[0])

    for i in range(len(target)):
        correct_index = len(target) - i - 1
        if target[correct_index] == '0':
            oracle_circuit.x(x[i])

    oracle_circuit.to_gate()

    return oracle_circuit
