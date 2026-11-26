# x25519 e migração pós-quântica

Experimento didático sobre a vulnerabilidade teórica do X25519 ao algoritmo de Shor e a migração para ML-KEM-768.

## Conteúdo

- `src/`: experimento ECDLP e benchmarks criptográficos.
- `data/`: resultados e tabelas.
- `figures/`: gráficos.
- `relatorio_tecnico.md`: relatório do trabalho.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução

```bash
python src/toy_ecdlog.py --output data/toy_ecdlog_results.json
python src/benchmark_pqc.py --repetitions 30 --output data/benchmark_pqc.json
python src/benchmark_sizes.py
```

Os tempos dependem do ambiente e devem ser medidos novamente na máquina de execução.

## Limite experimental

O experimento ECDLP atual é uma demonstração idealizada em curva pequena; não quebra Curve25519 real. Resultados toy não devem ser apresentados como ataque a chaves X25519 de produção.

## Referências

- [RFC 7748 — X25519](https://www.rfc-editor.org/rfc/rfc7748)
- [NIST FIPS 203 — ML-KEM](https://doi.org/10.6028/NIST.FIPS.203)
- Shor, P. W. (1994), *Algorithms for quantum computation: discrete logarithms and factoring*.
