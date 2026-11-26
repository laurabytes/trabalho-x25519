# avaliação experimental do x25519 e migração pós-quântica

**disciplina:** computação quântica e defesa  
**tema:** x25519, ecdlp, shor e ml-kem-768  
**integrantes:** ______________________________

## resumo

o trabalho estuda a relação entre x25519 e o problema do logaritmo discreto em curvas elípticas (ecdlp), simula instâncias reduzidas e compara x25519 com ml-kem-768. a simulação é ideal e não representa a quebra de curve25519 real. a migração é analisada em tamanho, comunicação e processamento.

## 1. algoritmo e problema matemático

x25519 é um mecanismo de acordo de chaves baseado em curve25519. sua segurança clássica está relacionada ao ecdlp: dados um ponto público (p) e (q=d p), recuperar o escalar secreto (d).

o algoritmo de shor resolve o logaritmo discreto em grupos abelianos em um computador quântico tolerante a falhas e suficientemente grande. isso representa uma vulnerabilidade teórica de x25519, não uma quebra por computadores quânticos atuais.

## 2. experimento reduzido

o script `src/ecdlog_shor.py` avalia quatro curvas curtas de weierstrass em corpos pequenos. para cada curva, calcula (q=3p), constrói a função (f(u,v)=[u]p+[v]q), aplica uma qft exata à representação do estado e recupera o escalar por amostras de fourier.

| instância | corpo | ordem | qubits lógicos do modelo | shots | segredo recuperado |
|---|---:|---:|---:|---:|---:|
| c4_f5 | 5 | 4 | 6 | 4.096 | 3 |
| c8_f5 | 5 | 8 | 9 | 4.096 | 3 |
| c16_f11 | 11 | 16 | 12 | 4.096 | 3 |
| c32_f23 | 23 | 32 | 15 | 4.096 | 3 |

a maior instância é c32_f23: (p=23), curva (y^2=x^3+x+10), (p=(5,5)), (q=(8,22)), ordem 32 e escalar de teste (d=3). em todas as instâncias, as amostras simuladas obedeceram à relação de período; aproximadamente metade foi informativa para a inversão modular.

**limite do experimento:** a implementação usa numpy, um oráculo por tabela de pontos e qft como matriz exata. não constrói nem transpila um circuito de portas no qiskit/aer, não mede profundidade ou contagem de gates e não modela ruído ou hardware. os números de qubits são do modelo lógico dos três registradores, não uma medição de circuito executável. o resultado demonstra a estrutura matemática em instâncias pequenas; não é uma execução completa em hardware nem uma quebra de curve25519.

## 3. alternativa pós-quântica

ml-kem-768 foi escolhido por preservar a função de estabelecimento de segredo compartilhado. é um mecanismo de encapsulamento padronizado no nist fips 203, com o fluxo:

1. **keygen:** gera as chaves.
2. **encaps:** gera ciphertext e segredo compartilhado.
3. **decaps:** recupera o segredo usando a chave privada.

ml-kem não é algoritmo de assinatura e não substitui certificados ou assinaturas digitais.

## 4. tamanhos e comunicação

os tamanhos abaixo são os comprimentos normativos dos elementos criptográficos, não arquivos pem:

| métrica | x25519 | ml-kem-768 | diferença |
|---|---:|---:|---:|
| chave pública | 32 b | 1.184 b | +3.600% |
| chave privada bruta | 32 b | 2.400 b | +7.400% |
| mensagem de troca considerada | 64 b (duas shares) | 1.088 b (ciphertext) | +1.600% |
| segredo compartilhado | 32 b | 32 b | 0% |

**cenário:** em 1 milhão de sessões, duas shares públicas x25519 por sessão totalizam 64.000.000 bytes. para ml-kem-768, um ciphertext por sessão e uma chave pública provisionada uma vez totalizam 1.088.001.184 bytes. a diferença é 1.024.001.184 bytes. o cenário não inclui cabeçalhos, certificados, retransmissões ou outras mensagens do protocolo.

## 5. processamento

benchmark de 30 repetições em linux x86-64, python 3.13.5 e openssl 3.5.5:

| operação | mediana |
|---|---:|
| x25519: gerar dois pares de chaves | 0,062113 ms |
| x25519: duas derivações | 0,064371 ms |
| ml-kem-768: keygen + exportação | 10,117555 ms |
| ml-kem-768: encaps | 4,851460 ms |
| ml-kem-768: decaps | 4,571113 ms |

os 30 testes de ml-kem-768 confirmaram igualdade entre os segredos encapsulado e desencapsulado. atenção: x25519 foi medido pela biblioteca python `cryptography`, enquanto ml-kem foi medido pela cli do openssl. os tempos incluem overheads diferentes e não permitem comparar diretamente a velocidade intrínseca das primitivas. cpu, memória e energia não foram medidos.

## 6. impacto e estratégia de migração

a migração exige atualizar bibliotecas e protocolos, negociar suporte ao kem, adaptar formatos e buffers, rever limites de mensagens e mtu, atualizar armazenamento e rotação de chaves e testar interoperabilidade. em dispositivos iot, também é necessário medir memória, cpu, energia e latência em hardware real.

uma implantação gradual pode incluir modo híbrido, desde que use uma composição e um protocolo especificados. a troca de x25519 por ml-kem não substitui a autenticação por assinatura digital.

## 7. respostas ao enunciado

**q1. maior instância:** c32_f23, ordem 32, escalar de teste 3 recuperado na simulação ideal, 15 qubits lógicos no modelo e 4.096 shots. não é uma chave curve25519 real.

**q2. fator limitante:** o custo exponencial da representação de estado e o crescimento do oráculo por tabela. não foram medidos limites de profundidade ou gates nativos.

**q3. vulnerabilidade:** x25519 depende do ecdlp, que shor resolve em um computador quântico tolerante a falhas com recursos suficientes.

**q4. alternativa:** ml-kem-768, pois fornece encapsulamento de chaves e preserva a função de estabelecimento de segredo compartilhado.

**q5. custo:** chave pública: 32 para 1.184 bytes; chave privada bruta: 32 para 2.400 bytes; mensagem considerada: 64 para 1.088 bytes. no cenário de um milhão de sessões, o acréscimo é 1.024.001.184 bytes. os tempos medidos estão na seção 5.

**q6. alterações necessárias:** bibliotecas, negociação de protocolo, formatos, buffers, armazenamento, rotação, limites de mensagens e testes de interoperabilidade.

**q7. basta trocar o algoritmo?** não. é necessário adaptar protocolo e arquitetura, testar compatibilidade e avaliar memória, processamento, energia e comunicação.

## conclusão

a simulação reduzida recuperou o escalar de teste nas quatro instâncias, mas não equivale a um circuito qiskit/aer transpilado nem à quebra de curve25519. o benchmark executou x25519 e ml-kem-768 e validou os segredos nos dois lados. ml-kem-768 mantém a função de estabelecimento de chaves, mas aumenta os tamanhos de chaves e mensagens e exige mudanças de software e arquitetura.

## referências

1. ietf. **rfc 7748 — elliptic curves for security**. 2016. https://www.rfc-editor.org/rfc/rfc7748
2. nist. **fips 203 — module-lattice-based key-encapsulation mechanism standard**. 2024. https://doi.org/10.6028/nist.fips.203
3. shor, p. w. **algorithms for quantum computation: discrete logarithms and factoring**. 1994.
4. material da disciplina. **exercício — avaliação experimental de algoritmos criptográficos frente ao algoritmo de shor e migração pós-quântica**. 2026.
