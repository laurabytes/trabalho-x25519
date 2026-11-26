# apresentação — x25519, shor e migração pós-quântica

> Roteiro em formato Markdown, organizado em slides. Pode ser convertido para PowerPoint/LibreOffice; os dados e gráficos citados estão no repositório.

---

## Slide 1 — título

**X25519: vulnerabilidade quântica e migração pós-quântica**

ECDLP, estrutura de Shor e comparação com ML-KEM-768.

---

## Slide 2 — objetivo

- Investigar o problema matemático associado ao X25519.
- Construir instâncias reduzidas de ECDLP.
- Simular a estrutura matemática de Shor.
- Comparar o mecanismo clássico com ML-KEM-768.
- Quantificar impactos de tamanho e comunicação.

---

## Slide 3 — X25519 e ECDLP

- X25519 é um mecanismo de acordo de chaves baseado em Curve25519.
- Problema subjacente: dado (P) e (Q=[d]P), recuperar (d).
- Shor resolve o logaritmo discreto em grupos abelianos em um computador quântico suficientemente capaz.

---

## Slide 4 — experimento reduzido

Quatro curvas pequenas foram avaliadas:

| instância | corpo | ordem | qubits abstratos |
|---|---:|---:|---:|
| C4_F5 | 5 | 4 | 6 |
| C8_F5 | 5 | 8 | 9 |
| C16_F11 | 11 | 16 | 12 |
| C32_F23 | 23 | 32 | 15 |

Em todas, o escalar de teste (d=3) foi recuperado na simulação.

---

## Slide 5 — maior instância

**C32_F23**

- Curva: (y^2=x^3+x+10 pmod{23})
- (P=(5,5)), (Q=(8,22))
- Ordem de (P): 32
- Escalar: 3
- 4.096 shots; 15 qubits lógicos abstratos

Não há profundidade nem contagem de portas: o programa usa NumPy, oráculo clássico e QFT matricial, não um circuito transpilado.

---

## Slide 6 — limite experimental

- Estado e QFT matricial crescem rapidamente.
- Oráculo calculado por tabela clássica.
- Sem ruído, conectividade ou execução em hardware.
- Não quebra Curve25519 nem chaves reais.

O experimento ilustra a estrutura matemática em instâncias pequenas.

---

## Slide 7 — alternativa pós-quântica

**ML-KEM-768**

1. KeyGen: gera chaves pública e privada.
2. Encaps: gera ciphertext e segredo compartilhado.
3. Decaps: recupera o mesmo segredo.

É um KEM para estabelecimento de segredo, não um algoritmo de assinatura.

---

## Slide 8 — tamanhos

| elemento | X25519 | ML-KEM-768 |
|---|---:|---:|
| chave pública | 32 B | 1.184 B |
| chave privada bruta | 32 B | 2.400 B |
| mensagem considerada | 64 B | 1.088 B |
| segredo compartilhado | 32 B | 32 B |

Tamanhos normativos dos elementos, não arquivos PEM.

---

## Slide 9 — comunicação

Cenário ilustrativo de 1 milhão de sessões:

- X25519: 64.000.000 B.
- ML-KEM-768: 1.088.001.184 B.
- Acréscimo: 1.024.001.184 B.

Considera duas shares X25519 por sessão e uma chave pública ML-KEM provisionada uma vez mais um ciphertext por sessão.

---

## Slide 10 — processamento e arquitetura

- Benchmark disponível em `data/benchmark_pqc.json`.
- X25519 usa Python `cryptography`; ML-KEM usa OpenSSL CLI.
- Overheads diferentes impedem comparação direta da velocidade intrínseca.
- Migração requer atualização de bibliotecas, protocolos, formatos, buffers, armazenamento e testes de interoperabilidade.
- Em IoT: medir CPU, memória, energia e latência no hardware-alvo.

---

## Slide 11 — respostas e conclusão

- Shor ameaça matematicamente ECC em computadores quânticos tolerantes a falhas.
- O experimento reduzido não equivale a ataque a parâmetros reais.
- ML-KEM-768 preserva a função de estabelecimento de segredo, mas aumenta tamanhos.
- Trocar a primitiva não basta: protocolo e arquitetura também precisam evoluir.

**Mensagem central:** a migração PQC envolve armazenamento, comunicação, processamento e arquitetura.
