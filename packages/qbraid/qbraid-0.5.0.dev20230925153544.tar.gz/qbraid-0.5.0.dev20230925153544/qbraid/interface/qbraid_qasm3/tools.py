# Copyright (C) 2023 qBraid
#
# This file is part of the qBraid-SDK
#
# The qBraid-SDK is free software released under the GNU General Public License v3
# or later. You can redistribute and/or modify it under the terms of the GPL v3.
# See the LICENSE file in the project root or <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# THERE IS NO WARRANTY for the qBraid-SDK, as per Section 15 of the GPL v3.

"""
Module containing OpenQASM 3 tools

"""
import os
import re
from typing import List

import numpy as np
from openqasm3 import dumps
from openqasm3.ast import QubitDeclaration
from openqasm3.parser import parse
from qiskit.qasm3 import loads

from qbraid.interface.qbraid_qiskit.tools import _unitary_from_qiskit

QASMType = str


def qasm3_qubits(qasmstr: str) -> List[QASMType]:
    """Get number of qasm qubits.

    Args:
        qasmstr (str): OpenQASM 3 string

    Returns:
        List of qubits in the circuit
    """
    program = parse(qasmstr)

    qubits = []
    for statement in program.statements:
        if isinstance(statement, QubitDeclaration):
            name = statement.qubit.name
            size = statement.size.value if statement.size else 1
            qubits.append((name, size))
    return qubits


def qasm3_num_qubits(qasmstr: str) -> int:
    """Calculate number of qubits in a qasm3 string"""
    program = parse(qasmstr)

    num_qubits = 0
    for statement in program.statements:
        if isinstance(statement, QubitDeclaration):
            num_qubits += statement.size.value
    return num_qubits


def qasm3_depth(qasmstr: str) -> int:
    """Calculates circuit depth of OpenQASM 3 string"""
    return loads(qasmstr).depth()


def _unitary_from_qasm3(qasmstr: QASMType) -> np.ndarray:
    """Return the unitary of the QASM 3 string"""
    circuit = loads(qasmstr)
    return _unitary_from_qiskit(circuit)


def _unitary_from_openqasm_ast(qasm_ast):
    """Return unitary of openqasm AST program"""
    qasm_3 = dumps(qasm_ast)
    return _unitary_from_qasm3(qasm_3)


def _remove_gate_definitions(qasm_str):
    """This is required to account for the case when the gate
     definition has an argument which is having same name as a
     quantum register

     now, if any gate is applied on this argument, it will be
     interpreted as being applied on THE WHOLE register, when it is
     only applied on the argument.

    Example :

    gate custom q1 {
        x q1; // this is STILL DETECTED as a gate application on q1
    }
    qreg q1[4];
    qreg q2[2];
    custom q1[0];
    cx q1[1], q2[1];

    // Actual depth : 1
    // Calculated depth : 2 (because of the gate definition)

    Args:
        qasm_str (string): The qasm string
    Returns:
        qasm_str (string): The qasm string with gate definitions removed
    """

    gate_decls = [x.group() for x in re.finditer(r"(gate)(.*\n)*?\s*\}", qasm_str)]
    for decl in gate_decls:
        qasm_str = qasm_str.replace(decl, "")
    return qasm_str


def _get_unused_qubit_indices(qasm_str, register_list):
    """Get unused qubit indices in the circuit

    Args:
        qasm_str (string): The qasm string
        register_list (list): The list of quantum registers with sizes

    Returns:
        dict: A dictionary with keys as register names and values as sets of unused indices
    """
    qasm_str = _remove_gate_definitions(qasm_str)
    lines = qasm_str.splitlines()
    gate_lines = [
        s
        for s in lines
        if s.strip() and not s.strip().startswith(("OPENQASM", "include", "qreg", "qubit", "//"))
    ]
    unused_indices = {}
    for qreg, size in register_list:
        unused_indices[qreg] = set(range(size))

        for line in gate_lines:
            if qreg not in line:
                continue
            # either qubits or full register is referenced
            used_indices = {int(x) for x in re.findall(rf"{qreg}\[(\d+)\]", line)}
            if len(used_indices) > 0:
                unused_indices[qreg] = unused_indices[qreg].difference(used_indices)
            else:
                # full register is referenced
                unused_indices[qreg] = set()
                break

            if len(unused_indices[qreg]) == 0:
                break

    return unused_indices


def _expand_to_contiguous_qasm3(qasmstr: str) -> QASMType:
    """Converts OpenQASM 3 string to contiguous qasm3 string with gate expansion

       no loops OR custom functions supported at the moment

    Args:
        qasmstr (str): OpenQASM 3 string

    Returns:
        str: Contiguous OpenQASM 3 string with gate expansion
    """

    # pylint: disable=import-outside-toplevel

    # 1. Analyse the qasm3 string for registers and find unused qubits
    qreg_list = qasm3_qubits(qasmstr)
    qubit_indices = _get_unused_qubit_indices(qasmstr, qreg_list)
    expansion_qasm = ""

    # 2. Add an identity gate for the unused qubits
    for reg, indices in qubit_indices.items():
        for index in indices:
            expansion_qasm += f"i {reg}[{index}];\n"

    # 4. Return the qasm3 string
    return qasmstr + expansion_qasm


def _remap_qubits(qasm_str, reg_name, reg_size, unused_indices):
    """Re-map the qubits for a partially used quantum register
    Args:
        qasm_str (str): QASM string
        reg_name (str): name of register
        reg_size (int): original size of register
        unused_indices (set): set of unused indices

    Returns:
        str: updated qasm string"""
    required_size = reg_size - len(unused_indices)

    new_id = 0
    qubit_map = {}
    for idx in range(reg_size):
        if idx not in unused_indices:
            # idx -> new_id
            qubit_map[idx] = new_id
            new_id += 1

    # old_id WILL NEVER match the declaration
    # as it will be < the original size of register

    # 1. Replace the qubits first
    #    as the regex may match the new declaration itself
    for old_id, new_id in qubit_map.items():
        if old_id != new_id:
            qasm_str = re.sub(rf"{reg_name}\s*\[{old_id}\]", f"{reg_name}[{new_id}]", qasm_str)

    # 2. Replace the declaration
    qasm_str = re.sub(
        rf"qreg\s+{reg_name}\s*\[{reg_size}\]\s*;",
        f"qreg {reg_name}[{required_size}];",
        qasm_str,
    )
    qasm_str = re.sub(
        rf"qubit\s*\[{reg_size}\]\s*{reg_name}\s*;",
        f"qubit[{required_size}] {reg_name};",
        qasm_str,
    )
    # 1 qubit register can never be partially used :)

    return qasm_str


def _compress_to_contiguous_qasm3(qasm_str: str) -> QASMType:
    """Converts OpenQASM 3 string to contiguous qasm3 string by removing unused qubits

    Args:
        qasmstr (str): OpenQASM 3 string

    Returns:
        QASMType: Contiguous OpenQASM 3 string
    """

    qreg_list = set(qasm3_qubits(qasm_str))
    qubit_indices = _get_unused_qubit_indices(qasm_str, qreg_list)
    for reg, indices in qubit_indices.items():
        size = 1
        for qreg in qreg_list:
            if qreg[0] == reg:
                size = qreg[1]
                break

        # remove the register declarations which are not used
        if len(indices) == size:
            qasm_str = re.sub(rf"qreg\s+{reg}\s*\[\d+\]\s*;", "", qasm_str)
            qasm_str = re.sub(rf"qubit\s*\[\d+\]\s*{reg}\s*;", "", qasm_str)
            if size == 1:
                qasm_str = re.sub(rf"qubit\s+{reg}\s*;", "", qasm_str)
            qreg_list.remove((reg, size))

        # resize and re-map the indices of the partially used register
        elif len(indices):
            qasm_str = _remap_qubits(qasm_str, reg, size, indices)
    return qasm_str


def _convert_to_contiguous_qasm3(qasmstr: QASMType, expansion=False) -> QASMType:
    """Delete qubit(s) with no gate, if any exist."""
    # remove unused registers
    if not expansion:
        return _compress_to_contiguous_qasm3(qasmstr)
    return _expand_to_contiguous_qasm3(qasmstr)


def _build_qasm_3_reg(line: str, qreg_type: bool) -> QASMType:
    """Helper function to build openqasm 3 register statements

    Args:
        line (str): openqasm 2  regdecl statement
        qreg_type (bool): whether a qreg or creg type statement

    Returns:
        str : openqasm 3 qubits / bits declaration
    """
    reg_keyword_len = 4
    line = line[reg_keyword_len:]
    elements = line.split("[")
    reg_name = elements[0].strip()
    reg_size = elements[1].split("]")[0].strip()
    result = "qubit" if qreg_type else "bit"
    result += f"[{reg_size}] {reg_name};\n"
    return result


def _build_qasm_3_measure(line: str) -> QASMType:
    """Helper function to build openqasm 3 measure string

    Args:
        line (str): openqasm 2 measure statement

    Returns:
        str:  openqasm 3 measure statement
    """
    measure_keyword_len = 7
    line = line[measure_keyword_len:]
    elements = line.split("->")
    qubits_name = elements[0].replace(" ", "")
    bits_name = elements[1].split(";")[0].replace(" ", "")

    return f"{bits_name} = measure {qubits_name};\n"


def _change_to_qasm_3(line: str) -> QASMType:
    """Function to change an openqasm 2 line to openqasm 3

    Args:
        line (str): an openqasm 2 line

    Returns:
        str: corresponding openqasm 3 line
    """
    # pylint: disable=import-outside-toplevel
    from qbraid.interface.qbraid_qasm.qelib1_defs import _decompose_rxx_instr

    line = line.lstrip()
    if line.startswith("OPENQASM"):
        return ""
    if "qelib1.inc" in line:
        return ""
    if line.startswith("qreg"):
        return _build_qasm_3_reg(line, qreg_type=True)
    if line.startswith("creg"):
        return _build_qasm_3_reg(line, qreg_type=False)
    if line.startswith("u("):
        return line.replace("u(", "U(")
    if line.startswith("rxx("):
        return _decompose_rxx_instr(line)
    if line.startswith("measure"):
        return _build_qasm_3_measure(line)
    if line.startswith("opaque"):
        # as opaque is ignored by openqasm 3 add it as a comment
        return "// " + line + "\n"
    return line + "\n"


def convert_to_qasm3(qasm2_str: str):
    """Convert a QASM 2.0 string to QASM 3.0 string

    Args:
        qasm2_str (str): QASM 2.0 string
    """
    # pylint: disable=import-outside-toplevel
    from qiskit import QuantumCircuit

    try:
        # use inbuilt method to check validity
        _ = QuantumCircuit.from_qasm_str(qasm2_str)
    except Exception as e:
        raise ValueError("Invalid QASM 2.0 string") from e

    qasm3_str = "OPENQASM 3.0;\ninclude 'stdgates.inc';"

    # add the gate from qelib1.inc not present in the stdgates.inc file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(
        os.path.join(current_dir, "qelib_qasm3.qasm"), mode="r", encoding="utf-8"
    ) as gate_defs:
        for line in gate_defs:
            qasm3_str += line

    for line in qasm2_str.splitlines():
        line = _change_to_qasm_3(line)
        qasm3_str += line
    return qasm3_str
