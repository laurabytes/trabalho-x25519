# x25519 e migração pós-quântica

estudo reduzido de ecdlp/shor e comparação de x25519 com ml-kem-768.

## executar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/ecdlog_shor.py --shots 4096
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python -m unittest discover -s tests
```

o benchmark pqc requer openssl 3.5+ com suporte a ml-kem-768.

## arquivos

- `src/`: experimentos e benchmarks.
- `data/`: resultados gerados.
- `figures/`: gráfico de comunicação.
- `relatorio_tecnico.md`: análise e limitações.

## limite

o ecdlp usa simulação ideal numpy, com oráculo por tabela e qft exata. não é circuito transpilado no qiskit/aer e não quebra curve25519 real. os tempos de benchmark incluem overhead das interfaces utilizadas.
