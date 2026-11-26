# x25519 e migração pós-quântica

Estudo de ECDLP em curvas elípticas pequenas, estrutura matemática de Shor e comparação de X25519 com ML-KEM-768.

## Requisitos

- Python 3.10 ou superior.
- Dependências de `requirements.txt`.
- OpenSSL 3.5 ou superior com ML-KEM-768 habilitado para executar o benchmark PQC completo.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Reprodução

Na raiz do repositório:

```bash
python src/ecdlog_qiskit.py --shots 4096 --secret 3 --seed 20261126
python src/ecdlog_shor.py --shots 4096 --secret 3 --seed 20261110
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python src/validate_artifacts.py
python -m unittest discover -s tests -v
```

O primeiro comando constrói, transpila e executa o circuito ECDLP em Qiskit/Aer, registrando distribuição de medições, profundidade, operações totais, portas de dois qubits e tempos. O segundo é uma simulação NumPy de referência para comparação matemática. Os comandos seguintes executam o benchmark PQC, atualizam tabelas/gráficos e validam os dados. O workflow reproduz também o circuito Qiskit/Aer e executa os testes.

## Estrutura

- `src/`: circuito ECDLP em Qiskit/Aer, simulação NumPy de referência, benchmark PQC, comparação de tamanhos e validação.
- `tests/`: testes automatizados.
- `data/`: dados em JSON e CSV.
- `figures/`: gráficos SVG.
- `notebooks/roteiro_experimental.md`: roteiro de execução.
- `relatorio_tecnico.md`: análise, resultados e limitações.
- `apresentacao.md`: conteúdo organizado em slides.

## Escopo e limitações

O experimento principal `src/ecdlog_qiskit.py` constrói um circuito quântico reversível para ECDLP em curvas pequenas, com oráculo de consulta por tabela implementado por portas multi-controladas, QFT inversa, transpilation e execução no AerSimulator. Registra métricas reais do circuito transpilado e distribuição de medições. O oráculo usa uma tabela clássica, portanto é uma implementação didática reduzida, não aritmética de curva escalável. Aer é simulação ideal, sem ruído nem execução em QPU. `src/ecdlog_shor.py` permanece como modelo NumPy independente para comparação.

A simulação demonstra a relação matemática em instâncias reduzidas; não quebra Curve25519 nem chaves X25519 reais. Os tempos de X25519 e ML-KEM-768 usam interfaces diferentes (biblioteca Python e CLI OpenSSL), portanto incluem overheads distintos e não devem ser interpretados como comparação isolada da velocidade das primitivas.

Os dados versionados devem ser considerados resultados de referência até que os comandos de reprodução e validação sejam executados no ambiente de avaliação. Consulte `data/environment.txt` e o relatório antes de comparar tempos.
