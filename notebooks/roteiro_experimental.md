# roteiro experimental

## executar

```bash
python src/ecdlog_shor.py --shots 4096 --seed 20261110
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python -m unittest discover -s tests
```

o primeiro script gera o resumo e a distribuição de medições em `data/`. o segundo executa x25519 e ml-kem-768; requer openssl 3.5+ com suporte a ml-kem-768. o terceiro atualiza as tabelas e o gráfico de comunicação.

a simulação ecdlp usa numpy, oráculo por tabela e qft exata. não é circuito transpilado no qiskit/aer, não inclui ruído e não quebra curve25519 real. os tempos de benchmark incluem overhead das interfaces.
