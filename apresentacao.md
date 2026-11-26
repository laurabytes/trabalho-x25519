# apresentação — x25519 e migração pós-quântica

## slide 1 — tema

**x25519, algoritmo de shor e migração pós-quântica**

experimento reduzido de ECDLP e comparação com ML-KEM-768.

## slide 2 — objetivo

- estudar a relação entre x25519 e o ECDLP;
- executar instâncias pequenas em Qiskit/Aer;
- observar a recuperação de um escalar conhecido;
- comparar tamanhos e tempos de x25519 e ML-KEM-768.

## slide 3 — x25519 e ECDLP

- x25519 é usado para estabelecer um segredo compartilhado.
- o problema estudado é: dado P e Q = [d]P, recuperar d.
- shor resolve o logaritmo discreto em um computador quântico suficientemente grande e tolerante a falhas.

## slide 4 — experimento

foram usadas quatro instâncias de curvas pequenas:

| instância | corpo | ordem | qubits lógicos |
|---|---:|---:|---:|
| C4_F5 | 5 | 4 | 6 |
| C8_F5 | 5 | 8 | 9 |
| C16_F11 | 11 | 16 | 12 |
| C32_F23 | 23 | 32 | 15 |

o escalar de teste d = 3 foi recuperado nas quatro instâncias.

## slide 5 — maior instância

**C32_F23**

- curva: y² = x³ + x + 10 (mod 23);
- P = (5, 5) e Q = (8, 22);
- ordem de P: 32;
- 15 qubits lógicos e 8 ancillas na síntese;
- 1.024 shots.

## slide 6 — métricas do circuito

na maior instância, a síntese para a base {u, cx} resultou em:

- 23 qubits transpilados;
- profundidade: 322.591;
- 417.102 operações;
- 138.292 portas CX.

## slide 7 — limitações

- o oráculo reversível usa uma tabela clássica;
- não há aritmética de curva escalável;
- a simulação no Aer é ideal, sem ruído;
- não foi usada uma QPU;
- o experimento não quebra Curve25519 nem chaves reais.

## slide 8 — ML-KEM-768

ML-KEM-768 é um mecanismo de encapsulamento de chaves.

1. **KeyGen:** gera as chaves.
2. **Encaps:** gera o ciphertext e o segredo compartilhado.
3. **Decaps:** recupera o segredo compartilhado.

é uma alternativa para estabelecimento de segredo, não um algoritmo de assinatura.

## slide 9 — tamanhos

| elemento | x25519 | ML-KEM-768 |
|---|---:|---:|
| chave pública | 32 B | 1.184 B |
| chave privada bruta | 32 B | 2.400 B |
| mensagem considerada | 32 B | 1.088 B |
| segredo compartilhado | 32 B | 32 B |

## slide 10 — comunicação

para 1 milhão de estabelecimentos, considerando uma chave pública x25519 ou um ciphertext ML-KEM-768 por estabelecimento:

- x25519: 32.000.000 B;
- ML-KEM-768: 1.088.000.000 B;
- diferença: 1.056.000.000 B.

o cenário não inclui cabeçalhos ou outras mensagens do protocolo.

## slide 11 — benchmark

foram feitas 30 repetições.

| operação | mediana |
|---|---:|
| x25519 — geração de par | 0,062729 ms |
| x25519 — dois exchanges | 0,063765 ms |
| ML-KEM-768 — KeyGen e exportação | 6,813892 ms |
| ML-KEM-768 — Encaps | 3,343627 ms |
| ML-KEM-768 — Decaps | 2,984659 ms |

x25519 foi medido pela biblioteca Python cryptography e ML-KEM-768 pela CLI do OpenSSL. os tempos incluem overheads diferentes.

## slide 12 — conclusão

- o circuito recuperou d = 3 nas quatro instâncias reduzidas;
- as métricas mostram o custo da síntese do oráculo usado;
- ML-KEM-768 aumenta os tamanhos de chave e mensagem;
- a migração exige avaliar protocolos, armazenamento e recursos dos dispositivos.

**os resultados são de instâncias reduzidas e não representam um ataque a x25519 real.**
