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
Module defining BraketCircuit Class

"""
from braket.circuits.circuit import Circuit as BKCircuit

from qbraid.transpiler.programs.abc_qprogram import QuantumProgram


class BraketCircuit(QuantumProgram):
    """Wrapper class for Amazon Braket ``Circuit`` objects."""

    def __init__(self, circuit: BKCircuit):
        """Create a BraketCircuit

        Args:
            circuit: the circuit object to be wrapped

        """
        super().__init__(circuit)

        self._qubits = circuit.qubits
        self._num_qubits = len(self.qubits)
        self._depth = circuit.depth
        self._package = "braket"
        self._program_type = "Circuit"
