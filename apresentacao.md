# apresentação — x25519 e migração pós-quântica

## slide 1 — tema

**x25519, algoritmo de shor e migração pós-quântica**

experimento reduzido de ecdlp e comparação com ml-kem-768.

## slide 2 — objetivo

- estudar a relação entre x25519 e o ecdlp;
- executar instâncias pequenas em qiskit/aer;
- observar a recuperação de um escalar conhecido;
- comparar tamanhos e tempos de x25519 e ml-kem-768.

## slide 3 — x25519 e ecdlp

- x25519 é usado para estabelecer um segredo compartilhado.
- o problema estudado é: dado p e q = [d]p, recuperar d.
- shor resolve o logaritmo discreto em um computador quântico suficientemente grande e tolerante a falhas.

## slide 4 — experimento

foram usadas quatro instâncias de curvas pequenas:

| instância | corpo | ordem | qubits lógicos |
|---|---:|---:|---:|
| c4_f5 | 5 | 4 | 6 |
| c8_f5 | 5 | 8 | 9 |
| c16_f11 | 11 | 16 | 12 |
| c32_f23 | 23 | 32 | 15 |

o escalar de teste d = 3 foi recuperado nas quatro instâncias.

## slide 5 — maior instância

**c32_f23**

- curva: y² = x³ + x + 10 (mod 23);
- p = (5, 5) e q = (8, 22);
- ordem de p: 32;
- 15 qubits lógicos e 8 ancillas na síntese;
- 1.024 shots.

## slide 6 — métricas do circuito

na maior instância, a síntese para a base {u, cx} resultou em:

- 23 qubits transpilados;
- profundidade: 322.591;
- 417.102 operações;
- 138.292 portas cx.

## slide 7 — limitações

- o oráculo reversível usa uma tabela clássica;
- não há aritmética de curva escalável;
- a simulação no aer é ideal, sem ruído;
- não foi usada uma qpu;
- o experimento não quebra curve25519 nem chaves reais.

## slide 8 — ml-kem-768

ml-kem-768 é um mecanismo de encapsulamento de chaves.

1. **keygen:** gera as chaves.
2. **encaps:** gera o ciphertext e o segredo compartilhado.
3. **decaps:** recupera o segredo compartilhado.

é uma alternativa para estabelecimento de segredo, não um algoritmo de assinatura.

## slide 9 — tamanhos

| elemento | x25519 | ml-kem-768 |
|---|---:|---:|
| chave pública | 32 b | 1.184 b |
| chave privada bruta | 32 b | 2.400 b |
| mensagem considerada | 32 b | 1.088 b |
| segredo compartilhado | 32 b | 32 b |

## slide 10 — comunicação

para 1 milhão de estabelecimentos, considerando uma chave pública x25519 ou um ciphertext ml-kem-768 por estabelecimento:

- x25519: 32.000.000 b;
- ml-kem-768: 1.088.000.000 b;
- diferença: 1.056.000.000 b.

o cenário não inclui cabeçalhos ou outras mensagens do protocolo.

## slide 11 — benchmark

foram feitas 30 repetições.

| operação | mediana |
|---|---:|
| x25519 — geração de par | 0,062729 ms |
| x25519 — dois exchanges | 0,063765 ms |
| ml-kem-768 — keygen e exportação | 6,813892 ms |
| ml-kem-768 — encaps | 3,343627 ms |
| ml-kem-768 — decaps | 2,984659 ms |

x25519 foi medido pela biblioteca python cryptography e ml-kem-768 pela cli do openssl. os tempos incluem overheads diferentes.

## slide 12 — conclusão

- o circuito recuperou d = 3 nas quatro instâncias reduzidas;
- as métricas mostram o custo da síntese do oráculo usado;
- ml-kem-768 aumenta os tamanhos de chave e mensagem;
- a migração exige avaliar protocolos, armazenamento e recursos dos dispositivos.

**os resultados são de instâncias reduzidas e não representam um ataque a x25519 real.**
