#!/usr/bin/env python3
"""Circuito Qiskit de ECDLP reduzido: oráculo reversível por tabela e QFT."""
import argparse
import csv
import json
import math
import time
from pathlib import Path

import qiskit
import qiskit_aer
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFTGate
from qiskit_aer import AerSimulator

CASES = [
    {"name": "C4_F5", "p": 5, "a": 1, "b": 2, "P": (1, 2), "r": 4},
    {"name": "C8_F5", "p": 5, "a": 4, "b": 1, "P": (0, 1), "r": 8},
    {"name": "C16_F11", "p": 11, "a": 2, "b": 1, "P": (0, 1), "r": 16},
    {"name": "C32_F23", "p": 23, "a": 1, "b": 10, "P": (5, 5), "r": 32},
]


def point_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p)
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p)
    slope %= p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def point_mul(k, P, a, p):
    result, addend = None, P
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result


def point_order(P, a, p):
    current = None
    for order in range(1, 2 * p + 2):
        current = point_add(current, P, a, p)
        if current is None:
            return order
    raise ValueError("Ordem do ponto não encontrada.")


def inverse_qft(qc, register):
    """Aplica a QFT inversa padronizada do Qiskit ao registrador."""
    qc.append(QFTGate(len(register)).inverse(), register)
