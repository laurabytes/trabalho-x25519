# Roteiro experimental

Os scripts geram os resultados em `data/`. Registre o ambiente e mantenha os arquivos gerados junto da entrega.

## 1. ECDLP reduzido

```bash
python src/ecdlog_shor.py --shots 4096 --seed 20261110
```

O script executa quatro instâncias de curvas curtas de Weierstrass, calcula `Q=3P`, simula o oráculo de pontos e a QFT exata, amostra os pares de Fourier e recupera o escalar por inversão modular. A saída inclui os parâmetros, a fração de amostras informativas e a distribuição em CSV.

Limite: simulação ideal NumPy, sem transpilação Qiskit/Aer, ruído ou hardware. Não representa ataque a Curve25519 real.

## 2. Comparação criptográfica

```bash
python src/benchmark_pqc.py --repetitions 30
```

O fluxo valida X25519 nos dois sentidos e executa ML-KEM-768 em OpenSSL 3.5+: KeyGen, Encaps e Decaps. Os segredos são comparados byte a byte. Os tempos CLI incluem inicialização de processos e I/O.

## 3. Tamanhos e comunicação

```bash
python src/benchmark_sizes.py
```

O cenário usa duas shares públicas efêmeras X25519 por sessão e uma chave pública ML-KEM provisionada uma vez, mais um ciphertext por sessão.

## 4. Testes

```bash
python -m unittest discover -s tests
```

Registre SO, CPU, RAM, Python, OpenSSL e versões das bibliotecas. Não compare diretamente tempos obtidos por interfaces ou ambientes diferentes.
