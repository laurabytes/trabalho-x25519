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
python src/ecdlog_shor.py --shots 4096 --secret 3 --seed 20261110
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python src/validate_artifacts.py
python -m unittest discover -s tests -v
```

O primeiro comando gera os resultados agregados e a distribuição de medições em `data/`. O segundo executa X25519 e ML-KEM-768 e verifica se os dois lados obtêm o mesmo segredo. O terceiro atualiza as tabelas e gráficos de tamanhos/comunicação. O quarto verifica a consistência dos arquivos gerados.

## Estrutura

- `src/`: simulação ECDLP, benchmark PQC, comparação de tamanhos e validação.
- `tests/`: testes automatizados.
- `data/`: dados em JSON e CSV.
- `figures/`: gráficos SVG.
- `notebooks/roteiro_experimental.md`: roteiro de execução.
- `relatorio_tecnico.md`: análise, resultados e limitações.
- `apresentacao.md`: conteúdo organizado em slides.

## Escopo e limitações

O experimento ECDLP é uma simulação ideal em NumPy: usa operações de pontos em curvas pequenas, um oráculo clássico por tabela e QFT exata por matriz. **Não implementa um circuito quântico de portas, não é transpilado no Qiskit/Aer e não fornece profundidade nem contagem de gates.** Os qubits informados são a contagem lógica dos registradores abstratos do modelo.

A simulação demonstra a relação matemática em instâncias reduzidas; não quebra Curve25519 nem chaves X25519 reais. Os tempos de X25519 e ML-KEM-768 usam interfaces diferentes (biblioteca Python e CLI OpenSSL), portanto incluem overheads distintos e não devem ser interpretados como comparação isolada da velocidade das primitivas.

Os dados versionados devem ser considerados resultados de referência até que os comandos de reprodução e validação sejam executados no ambiente de avaliação. Consulte `data/environment.txt` e o relatório antes de comparar tempos.
