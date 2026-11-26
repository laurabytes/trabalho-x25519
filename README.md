# x25519 e migração pós-quântica

este projeto testa o ecdlp em curvas pequenas e compara x25519 com ml-kem-768.

## requisitos

- python 3.10 ou superior;
- dependências de `requirements.txt`;
- openssl 3.5 ou superior com ml-kem-768 habilitado.

## instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

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

## arquivos

- `src/`: programas dos experimentos e validação;
- `tests/`: testes;
- `data/`: resultados em json e csv;
- `figures/`: gráficos;
- `notebooks/roteiro_experimental.md`: passos para reproduzir;
- `relatorio_tecnico.md`: método, resultados e limitações;
- `apresentacao.md`: conteúdo dos slides.

## observações

o circuito no qiskit/aer testa quatro casos pequenos de ecdlp. o oráculo reversível usa uma tabela clássica e não implementa aritmética de curva escalável. a simulação é ideal e não usa uma qpu.

o experimento não quebra curve25519 nem chaves x25519 reais. os tempos de x25519 e ml-kem-768 vêm de interfaces diferentes e incluem overheads distintos. os resultados completos estão na pasta `data/` e no relatório.
