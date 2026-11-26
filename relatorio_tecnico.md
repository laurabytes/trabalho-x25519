# avaliação experimental do x25519 e migração pós-quântica

**disciplina:** computação quântica e defesa  
**tema:** x25519, ecdlp, shor e ml-kem-768  
**integrantes:** ______________________________

## resumo

Este trabalho analisa X25519, mecanismo de acordo de chaves baseado em Curve25519, por meio de instâncias reduzidas do problema do logaritmo discreto em curvas elípticas (ECDLP). Também apresenta uma simulação ideal da estrutura matemática associada a Shor e compara tamanhos e operações de X25519 e ML-KEM-768. O experimento reduzido não representa a quebra de uma chave real nem a execução de um circuito quântico em hardware.

## 1. algoritmo clássico e problema matemático

X25519 é uma função de acordo de chaves baseada em Curve25519. A segurança clássica do mecanismo está relacionada à dificuldade do problema do logaritmo discreto em curvas elípticas: dados um ponto base (P) e um ponto público (Q=[d]P), encontrar o escalar (d).

O algoritmo de Shor fornece um algoritmo quântico polinomial para o logaritmo discreto em grupos abelianos. Assim, um computador quântico tolerante a falhas e suficientemente grande ameaça a segurança de mecanismos ECC como X25519. Isso é uma vulnerabilidade matemática teórica, não uma quebra realizada por computadores quânticos atuais.

## 2. experimento reduzido com a estrutura de shor

O script `src/ecdlog_shor.py` avalia quatro curvas curtas de Weierstrass sobre corpos finitos pequenos. Para cada instância, define (Q=[3]P), constrói classicamente a função (f(u,v)=[u]P+[v]Q), representa os estados em NumPy e aplica a transformada de Fourier quântica como matriz exata. As amostras são então usadas para recuperar o escalar de teste.

| instância | corpo finito | ordem de P | qubits lógicos abstratos | shots | escalar recuperado |
|---|---:|---:|---:|---:|---:|
| C4_F5 | 5 | 4 | 6 | 4.096 | 3 |
| C8_F5 | 5 | 8 | 9 | 4.096 | 3 |
| C16_F11 | 11 | 16 | 12 | 4.096 | 3 |
| C32_F23 | 23 | 32 | 15 | 4.096 | 3 |

### maior instância

A maior instância modelada é C32_F23:

- corpo: (mathbb{F}_{23});
- curva: (y^2=x^3+x+10 pmod{23});
- ponto base: (P=(5,5));
- ponto público: (Q=(8,22));
- ordem de (P): 32;
- escalar de teste: (d=3);
- registradores de fase: 5 qubits em cada um;
- registrador de pontos: 5 qubits na representação abstrata;
- total: 15 qubits lógicos abstratos;
- medições configuradas: 4.096;
- recuperação: o escalar 3 é recuperado pela rotina clássica sobre as amostras.

A probabilidade empírica de sucesso do algoritmo completo deve ser entendida como resultado da execução com a semente escolhida, não como uma estimativa universal. A fração informativa teórica do primeiro registrador é (arphi(32)/32=0,5). A fração de amostras que satisfaz a relação de período e a distribuição efetivamente observada ficam registradas em `data/ecdlog_shor_results.json` e `data/ecdlog_shor_measurements.csv`.

**Profundidade e contagem de portas:** não se aplicam a esta implementação. O código não constrói um circuito de portas e, portanto, não é correto atribuir-lhe profundidade, total de gates ou gates de dois qubits. Também não há ruído, conectividade física, transpilation ou execução em FakeProvider/Aer. Os 15 qubits são uma contagem abstrata dos registradores do modelo, não uma estimativa de recursos de uma implementação física de Shor.

### limite experimental

A representação de estado cresce rapidamente com o tamanho dos registradores. Além disso, o oráculo é calculado classicamente por tabela de pontos e a QFT é aplicada como matriz densa. Esses fatores tornam o modelo inadequado para extrapolar diretamente recursos de hardware. A simulação demonstra a estrutura matemática em grupos pequenos, não uma implementação quântica completa nem a quebra de Curve25519 real.

## 3. alternativa pós-quântica

ML-KEM-768 foi escolhido por manter a função de estabelecimento de segredo compartilhado por encapsulamento. Seu fluxo é:

1. **KeyGen:** gera a chave pública e a chave de desencapsulamento.
2. **Encaps:** usa a chave pública para produzir ciphertext e segredo compartilhado.
3. **Decaps:** usa a chave privada e o ciphertext para recuperar o mesmo segredo.

ML-KEM é um mecanismo de encapsulamento de chaves (KEM), não um algoritmo de assinatura digital. A migração de X25519 para ML-KEM não substitui, por si só, os mecanismos de autenticação e assinatura do protocolo.

## 4. comparação de tamanhos e comunicação

A tabela usa os tamanhos dos elementos criptográficos padronizados, não o tamanho de arquivos PEM exportados pelo OpenSSL.

| métrica | X25519 | ML-KEM-768 | diferença |
|---|---:|---:|---:|
| chave pública | 32 B | 1.184 B | +1.152 B (+3.600%) |
| chave privada em formato bruto | 32 B | 2.400 B | +2.368 B (+7.400%) |
| mensagem considerada | 64 B (duas shares públicas) | 1.088 B (ciphertext) | +1.024 B (+1.600%) |
| segredo compartilhado | 32 B | 32 B | 0 B (0%) |

### cenário quantitativo

Considerando 1.000.000 de sessões, duas shares públicas X25519 por sessão totalizam 64.000.000 B. No cenário ML-KEM-768, considera-se um ciphertext por sessão e uma chave pública provisionada uma única vez: 1.088.001.184 B. O acréscimo calculado é 1.024.001.184 B.

Esse cenário é ilustrativo e considera apenas os elementos indicados. Não inclui cabeçalhos, certificados, retransmissões, armazenamento de chaves privadas, rotação ou outras mensagens do protocolo. Os dados estão em `data/communication_scenario.csv`.

## 5. processamento e reprodutibilidade

O script `src/benchmark_pqc.py` mede geração de chaves e operações de acordo/encapsulamento em repetições configuráveis. Ele também verifica a igualdade entre os segredos derivados pelos dois lados. O arquivo `data/benchmark_pqc.json` registra ambiente, versões, número de repetições, tamanhos observados e medianas.

**Atenção à comparação:** X25519 é medido pela biblioteca Python `cryptography`, enquanto ML-KEM-768 é medido pela interface de linha de comando do OpenSSL. Os tempos incluem overhead de interfaces, processos e arquivos, portanto não isolam o custo das primitivas e não devem ser comparados como benchmark justo de implementação. Os tamanhos PEM também não devem ser confundidos com os tamanhos normativos da seção 4. CPU, memória e energia não são medidos neste experimento.

Para obter uma medição atualizada no ambiente de avaliação, execute:

```bash
python src/benchmark_pqc.py --repetitions 30
```

Se OpenSSL não oferecer ML-KEM-768, o script registra a indisponibilidade em vez de simular um resultado.

## 6. impacto e estratégia de migração

A migração exige mais do que trocar uma primitiva. É necessário atualizar bibliotecas e versões de protocolos, negociar suporte ao KEM, adaptar formatos e tamanhos de chaves e ciphertexts, revisar buffers e limites de mensagens/MTU, atualizar armazenamento e rotação de chaves e testar interoperabilidade. Em dispositivos IoT, devem ser medidos consumo de memória, CPU, energia e latência no hardware-alvo.

Uma implantação gradual pode considerar um modo híbrido, desde que utilize uma composição e um protocolo especificados e analisados. A troca de X25519 por ML-KEM não elimina a necessidade de autenticação e de assinaturas digitais resistentes a ataques quânticos quando aplicável.

## 7. respostas ao enunciado

**Q1. Qual foi a maior instância comprometida experimentalmente?**  
A maior instância modelada foi C32_F23, com corpo (mathbb{F}_{23}), curva (y^2=x^3+x+10), (P=(5,5)), (Q=(8,22)), ordem 32 e escalar de teste (d=3). A rotina recupera o escalar nas amostras simuladas. O modelo usa 15 qubits lógicos abstratos e 4.096 shots. Não há profundidade ou contagem de gates porque não foi construído um circuito de portas.

**Q2. Qual foi o principal fator limitante?**  
O crescimento da representação de estado e o custo de calcular o oráculo por tabela e aplicar a QFT densa. O experimento não mediu recursos de circuito transpilado.

**Q3. Por que X25519 é vulnerável mesmo sem quebrar uma chave real?**  
Porque sua segurança está relacionada ao ECDLP, para o qual Shor oferece um algoritmo quântico eficiente em um computador tolerante a falhas e suficientemente grande. A instância reduzida ilustra a estrutura matemática, não os recursos necessários para atacar Curve25519.

**Q4. Qual alternativa PQC é adequada?**  
ML-KEM-768, padronizado para encapsulamento de chaves, mantém a função de estabelecer um segredo compartilhado. A autenticação e as assinaturas precisam ser tratadas separadamente.

**Q5. Qual é o custo quantitativo?**  
A chave pública passa de 32 B para 1.184 B; a chave privada bruta considerada, de 32 B para 2.400 B; a mensagem de troca considerada, de 64 B para 1.088 B. No cenário de um milhão de sessões, o volume modelado aumenta em 1.024.001.184 B. O processamento é registrado no JSON do benchmark, com a ressalva de que as interfaces são diferentes; CPU, memória e energia não foram medidos.

**Q6. Quais alterações são necessárias?**  
Atualizar bibliotecas, protocolos e negociação de algoritmos; adaptar formatos, buffers, armazenamento, rotação e limites de mensagens; e validar interoperabilidade e compatibilidade nos dispositivos.

**Q7. Basta substituir o algoritmo?**  
Não. A migração exige mudanças de protocolo e arquitetura, planejamento de provisionamento e armazenamento, tratamento de mensagens maiores, compatibilidade entre versões e avaliação de recursos dos dispositivos.

## conclusão

A simulação em quatro grupos pequenos recupera o escalar de teste e ilustra a relação matemática explorada por Shor. Como usa NumPy, oráculo clássico por tabela e QFT matricial, não fornece métricas de circuito quântico nem demonstra ataque a Curve25519. A comparação com ML-KEM-768 evidencia aumento de tamanhos e necessidades de adaptação de protocolo e arquitetura. A avaliação de processamento deve ser interpretada com cautela devido às interfaces diferentes e precisa ser reproduzida no ambiente de entrega.

## referências

1. IETF. **RFC 7748 — Elliptic Curves for Security**. 2016. https://www.rfc-editor.org/rfc/rfc7748
2. NIST. **FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard**. 2024. https://doi.org/10.6028/NIST.FIPS.203
3. Shor, P. W. **Algorithms for quantum computation: discrete logarithms and factoring**. 1994.
4. Material da disciplina. **Exercício — Avaliação Experimental de Algoritmos Criptográficos frente ao Algoritmo de Shor e Migração Pós-Quântica**. 2026.
