from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import QasmSimulator


def oracle(target):
    # Create quantum program that find 01101 by reversing its phase
    x = QuantumRegister(len(target), name='X')  # 5 qubits index 0 is the right most qubit
    ands_results = QuantumRegister(len(target) - 1, name='Ands_results')
    oracle_circuit = QuantumCircuit(x, ands_results, name='oracle')

    for i in range(len(target) - 1):
        correct_index = len(target) - i - 1
        if i == 0:
            if target[correct_index] == '0':
                oracle_circuit.x(x[i])
            if target[correct_index - 1] == '0':
                oracle_circuit.x(x[i + 1])

            oracle_circuit.ccx(x[i], x[i + 1], ands_results[i])

            if target[correct_index] == '0':
                oracle_circuit.x(x[i])
            if target[correct_index - 1] == '0':
                oracle_circuit.x(x[i + 1])

            continue

        if target[correct_index - 1] == '0':
            oracle_circuit.x(x[i + 1])

        oracle_circuit.ccx(ands_results[i - 1], x[i + 1], ands_results[i])

        if target[correct_index - 1] == '0':
            oracle_circuit.x(x[i + 1])

    oracle_circuit.cz(ands_results[len(target) - 2], x)
    # oracle_circuit.x(ands_results)
    oracle_circuit.to_gate()

    return oracle_circuit
