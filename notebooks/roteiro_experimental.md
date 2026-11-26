# Roteiro de execução e registro experimental

Este roteiro é um caderno textual de laboratório. Os comandos produzem arquivos JSON/CSV que podem ser anexados ao relatório.

## A. ECDLP toy

```bash
python src/toy_ecdlog.py --p 17 --a 2 --b 2 --secret 3 --shots 4096 --seed 2026
```

Anote a curva, P, Q, ordem, d e a distribuição. O script não executa circuito quântico. Para completar a exigência de Shor em circuito, construa um oráculo reversível para a ação do grupo e registre transpilation metrics do Qiskit Aer.

## B. X25519

```bash
python src/benchmark_pqc.py --repetitions 30
```

Confirme que os segredos dos dois lados coincidem. Reexecute pelo menos cinco vezes e informe mediana e dispersão.

## C. ML-KEM-768

Use uma implementação que exponha KeyGen, Encaps e Decaps (OpenSSL EVP, liboqs ou biblioteca auditada). Registre separadamente:
- tempo KeyGen;
- tempo Encaps;
- tempo Decaps;
- bytes da chave pública, chave privada e ciphertext;
- confirmação de igualdade dos segredos.

Não misture tempo de inicialização da biblioteca com tempo de operação sem declarar isso.

## D. Ambiente

Registre SO, CPU, RAM, Python, OpenSSL, bibliotecas e parâmetros. Não preencha métricas de circuito se não tiver um circuito real medido.
