# roteiro experimental

## ambiente

- Python 3.10 ou superior.
- Dependências listadas em `requirements.txt`.
- OpenSSL 3.5+ com suporte a ML-KEM-768 para o benchmark completo.

## execução

Na raiz do repositório:

```bash
python src/ecdlog_shor.py --shots 4096 --secret 3 --seed 20261110
python src/benchmark_pqc.py --repetitions 30
python src/benchmark_sizes.py
python src/validate_artifacts.py
python -m unittest discover -s tests -v
```

O script ECDLP grava `data/ecdlog_shor_results.json` e `data/ecdlog_shor_measurements.csv`. O benchmark PQC grava `data/benchmark_pqc.json`. A comparação de tamanhos atualiza os CSVs e gráficos em `figures/`. O validador verifica estrutura, contagem de shots, relações de período e consistência dos CSVs.

## interpretação

A implementação ECDLP usa NumPy, operações clássicas de pontos, oráculo por tabela e QFT exata por matriz. Não é um circuito de portas, não é transpilada em Qiskit/Aer e não mede profundidade ou contagem de gates. Não inclui ruído nem hardware. Os qubits são contagens abstratas dos registradores do modelo.

X25519 é executado pela biblioteca Python `cryptography`; ML-KEM-768, pela CLI do OpenSSL. Os tempos incluem overheads diferentes e não são comparação direta do desempenho intrínseco das primitivas. Se ML-KEM-768 não estiver disponível no OpenSSL local, o script registra essa indisponibilidade.
