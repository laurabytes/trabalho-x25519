# roteiro experimental

## ambiente

- python 3.10 ou superior;
- dependências de `requirements.txt`;
- openssl 3.5 ou superior com ML-KEM-768 para o benchmark completo.

## execução

na raiz do projeto:

```bash
python src/ecdlog_qiskit.py --shots 1024 --secret 3 --seed 20261126
python src/ecdlog_shor.py --shots 4096 --secret 3 --seed 20261110
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python src/validate_artifacts.py
python -m unittest discover -s tests -v
```

## arquivos gerados

- `data/ecdlog_qiskit_results.json` e `data/ecdlog_qiskit_measurements.csv`: resultados do circuito;
- `data/ecdlog_shor_results.json` e `data/ecdlog_shor_measurements.csv`: simulação numpy de referência;
- `data/benchmark_pqc.json`: amostras e medianas do benchmark;
- arquivos csv em `data/`: tamanhos e cenários;
- arquivos svg em `figures/`: gráficos.

## limitações

o circuito usa um oráculo reversível construído por tabela clássica. a simulação no Aer é ideal, sem ruído e sem execução em QPU. não representa um ataque a Curve25519 real.

os tempos de x25519 e ML-KEM-768 incluem overheads de interfaces diferentes. cpu e memória são registrados de forma agregada; energia não foi medida.
