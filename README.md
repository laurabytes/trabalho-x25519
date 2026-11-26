# x25519 e migração pós-quântica

Experimento reduzido sobre ECDLP/Shor e comparação de X25519 com ML-KEM-768.

## Estrutura

- `src/ecdlog_shor.py`: simulação ideal do ECDLP em curvas pequenas.
- `src/benchmark_pqc.py`: execução de X25519 e ML-KEM-768.
- `src/benchmark_sizes.py`: tabelas e cenário de comunicação.
- `data/`: resultados e medições.
- `relatorio_tecnico.md`: relatório técnico.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

O benchmark ML-KEM-768 também requer OpenSSL 3.5 ou superior com suporte ao algoritmo.

## Execução

```bash
python src/ecdlog_shor.py --shots 4096
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python -m unittest discover -s tests
```

## Limites

A simulação ECDLP usa estado vetorial NumPy, oráculo por tabela de pontos e QFT exata. Não é circuito nativo transpilado em Qiskit/Aer, não modela ruído e não quebra Curve25519 real. Os tempos do benchmark OpenSSL CLI incluem overhead de processos e arquivos; devem ser interpretados como medições do ambiente utilizado.

## Referências

- [RFC 7748 — X25519](https://www.rfc-editor.org/rfc/rfc7748)
- [NIST FIPS 203 — ML-KEM](https://doi.org/10.6028/NIST.FIPS.203)
- Shor, P. W. (1994). *Algorithms for quantum computation: discrete logarithms and factoring*.
