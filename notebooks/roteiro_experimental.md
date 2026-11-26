# Roteiro experimental

## Ambiente

- Python 3.10 ou superior.
- Dependências de `requirements.txt`, incluindo Qiskit e Qiskit Aer.
- OpenSSL 3.5+ com ML-KEM-768 habilitado para o benchmark completo.

## Execução

Na raiz do repositório:

```bash
python src/ecdlog_qiskit.py --shots 1024 --secret 3 --seed 20261126
python src/ecdlog_shor.py --shots 4096 --secret 3 --seed 20261110
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python src/validate_artifacts.py
python -m unittest discover -s tests -v
```

O circuito Qiskit/Aer grava `data/ecdlog_qiskit_results.json` e `data/ecdlog_qiskit_measurements.csv`, incluindo distribuição das medições, escalar recuperado, probabilidade empírica de candidato correto, qubits lógicos e transpilados, profundidade, operações totais, CX e tempos. A simulação NumPy é mantida como referência matemática independente.

O benchmark PQC grava `data/benchmark_pqc.json` com as amostras brutas e medianas de KeyGen, Encaps e Decaps, além de CPU/RSS agregados. A comparação de tamanhos gera `data/size_comparison.csv`, `data/communication_scenario.csv`, `data/storage_scenario.csv`, `data/ecdlog_qiskit_metrics.csv` e os gráficos SVG em `figures/`.

## Interpretação

O experimento principal usa um circuito Qiskit/Aer com oráculo reversível por tabela clássica, QFT inversa e pós-processamento clássico. Para medir recursos elementares, uma cópia equivalente usa síntese V-chain com ancillas e é transpilada para a base `{u, cx}`; a versão compacta equivalente é executada no AerSimulator ideal.

O oráculo não implementa aritmética de curva escalável. Aer não modela ruído físico nem execução em QPU. As métricas de portas correspondem ao oráculo reduzido sintetizado, não a uma estimativa de recursos para quebrar Curve25519 real.

X25519 é medido pela biblioteca Python `cryptography`; ML-KEM-768, pela CLI do OpenSSL. Os tempos incluem overheads diferentes e não são comparação direta do desempenho intrínseco das primitivas. CPU e RSS são agregados, não por operação; energia não é medida. Se ML-KEM-768 não estiver disponível no OpenSSL local, o script registra a indisponibilidade.
