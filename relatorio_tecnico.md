# Avaliação experimental do X25519 e migração pós-quântica

**Disciplina:** Computação Quântica e Defesa  
**Tema:** X25519, ECDLP, algoritmo de Shor e ML-KEM-768  
**Integrantes:** ______________________________________

## Resumo

Este trabalho analisa a vulnerabilidade teórica do mecanismo de acordo de chaves X25519 ao algoritmo de Shor e avalia ML-KEM-768 como alternativa pós-quântica. A parte experimental implementa instâncias reduzidas de ECDLP em circuito Qiskit, transpila o oráculo reversível para a base de portas {u, cx} e executa a versão compacta no AerSimulator. Foram avaliadas quatro ordens (4, 8, 16 e 32), recuperando d=3 em todas. A maior instância utilizou 15 qubits lógicos, 8 ancillas na síntese, 1.024 shots, profundidade 322.591 e 138.292 portas CX. O benchmark funcional X25519/ML-KEM-768 foi repetido 30 vezes, preservando amostras brutas, medianas e recursos agregados. O modelo é reduzido e não quebra Curve25519 real.

## 1. Introdução e problema matemático

X25519 é um mecanismo de acordo de chaves baseado na curva Curve25519. Duas partes geram valores privados, calculam chaves públicas e combinam o segredo local com a chave pública remota para obter o mesmo segredo compartilhado. O RFC 7748 define entradas e saídas de 32 bytes.

A segurança clássica está relacionada ao problema do logaritmo discreto em curvas elípticas (ECDLP): dados um ponto base P e um ponto público Q=[d]P, recuperar o escalar privado d. O algoritmo de Shor resolve o logaritmo discreto em grupos abelianos em tempo polinomial no modelo de computador quântico tolerante a falhas. Isso representa uma ameaça matemática a mecanismos ECC, mas não significa que computadores quânticos atuais consigam quebrar uma chave X25519 real.

## 2. Experimento reduzido de ECDLP com Shor em Qiskit/Aer

O experimento principal está implementado em `src/ecdlog_qiskit.py`. O circuito prepara dois registradores de fase em superposição, calcula reversivelmente a função de grupo f(u,v)=[u]P+[v]Q por um oráculo de consulta em tabela, aplica a QFT inversa e mede os registradores. O pós-processamento clássico usa as amostras de Fourier para recuperar o escalar de teste.

O oráculo é reversível e implementado com portas multi-controladas X. Para medir recursos em uma base elementar, uma cópia equivalente usa ancillas limpas na síntese V-chain e é transpilada para {u, cx}. A execução ideal das medições é feita no AerSimulator com a versão compacta equivalente do circuito. A síntese de métricas usa optimization_level=0; a execução no simulador usa optimization_level=1. Ambiente: Qiskit 1.4.6 e Qiskit Aer 0.17.2.

| Instância | p (bits) | Ordem r (bits) | P | Q | Qubits lógicos | Qubits transpilados | Profundidade | Operações totais | CX | Shots | P(correcta/shot) | d recuperado |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| C4_F5 | 5 (3) | 4 (2) | (1,2) | (1,3) | 6 | 8 | 679 | 892 | 298 | 1.024 | 48,44% | 3 |
| C8_F5 | 5 (3) | 8 (3) | (0,1) | (1,4) | 9 | 13 | 6.733 | 8.742 | 2.898 | 1.024 | 49,51% | 3 |
| C16_F11 | 11 (4) | 16 (4) | (0,1) | (8,1) | 12 | 18 | 50.199 | 64.992 | 21.540 | 1.024 | 50,00% | 3 |
| C32_F23 | 23 (5) | 32 (5) | (5,5) | (8,22) | 15 | 23 | 322.591 | 417.102 | 138.292 | 1.024 | 52,44% | 3 |

Em todas as quatro instâncias, a fração observada de amostras que satisfaz a relação de período foi 1,0 e o escalar d=3 foi recuperado. A probabilidade empírica de uma medição individual ser informativa e produzir o candidato correto variou de 48,44% a 52,44%; a recuperação final utiliza 1.024 shots. Os tamanhos de p e da ordem r em bits estão indicados entre parênteses na tabela. As contagens por par medido estão em `data/ecdlog_qiskit_measurements.csv`; os resultados completos em `data/ecdlog_qiskit_results.json`; e a tabela de métricas em `data/ecdlog_qiskit_metrics.csv`.

### Maior instância

A maior instância resolvida foi C32_F23:

- Corpo F23; curva y² = x³ + x + 10 (mod 23).
- P=(5,5), Q=(8,22), ordem de P igual a 32.
- Escalar conhecido e recuperado: d=3.
- Dois registradores de fase com 5 qubits cada e registrador de ponto com 5 qubits.
- 15 qubits lógicos, mais 8 ancillas limpas na síntese V-chain (23 qubits transpilados).
- 1.024 shots; profundidade 322.591; 417.102 operações totais, incluindo 138.292 CX; probabilidade empírica de candidato correto por shot: 52,44%.
- Tempo de transpilação para métricas: 1,791 s; tempo de transpilação do circuito compacto para Aer: 0,134 s; simulação: 0,166 s.

### Limitações experimentais

O oráculo usa uma tabela clássica de pontos e não implementa aritmética reversível escalável de curvas elípticas. A execução é ideal no AerSimulator: não modela ruído, conectividade/calibração de um backend físico nem execução em QPU. Assim, as métricas são da síntese do oráculo reduzido para {u, cx}, não uma estimativa de recursos para quebrar Curve25519 real. A simulação NumPy independente foi mantida como referência matemática em `src/ecdlog_shor.py`.

A fatoração anterior de N=77, com a=30, valida parte do fluxo de Shor, mas não é um ataque ao X25519 e não é contabilizada como resultado ECDLP neste trabalho.

## 3. Comparação com parâmetros reais\n\nO X25519 real opera sobre Curve25519, definida sobre um campo de 255 bits, e oferece aproximadamente 128 bits de segurança clássica. A maior instância deste experimento usa p=23 (5 bits) e ordem de subgrupo r=32 (5 bits). Portanto, o modelo reduzido é muito menor e serve para observar a estrutura matemática, não para estimar diretamente o custo de quebrar Curve25519.\n\nOs qubits lógicos representam os registradores do algoritmo reduzido. Os 23 qubits transpilados da maior instância incluem 8 ancillas para decompor o oráculo; não são uma estimativa de qubits físicos para um ataque real. Uma execução em escala real exigiria correção quântica de erros, muitos qubits físicos por qubit lógico, fidelidade alta de portas, controle de decoerência, conectividade adequada e circuitos aritméticos muito mais complexos.\n\n## 4. Alternativa pós-quântica: ML-KEM-768

ML-KEM-768 é um mecanismo de encapsulamento de chaves baseado em reticulados, padronizado pelo NIST no FIPS 203. Seu fluxo é:

1. **KeyGen:** gera a chave pública e a chave de desencapsulamento.
2. **Encaps:** usa a chave pública para produzir um ciphertext e um segredo compartilhado.
3. **Decaps:** usa a chave privada e o ciphertext para recuperar o mesmo segredo.

ML-KEM é um KEM, não um algoritmo de assinatura digital. A migração de X25519 para ML-KEM não substitui, por si só, os mecanismos de autenticação e assinatura do protocolo.

## 5. Comparação quantitativa de tamanhos, armazenamento e comunicação

A tabela utiliza tamanhos normativos dos elementos criptográficos, não arquivos PEM exportados pelo OpenSSL.

| Métrica | X25519 | ML-KEM-768 | Diferença |
|---|---:|---:|---:|
| Chave pública | 32 B | 1.184 B | +1.152 B (+3.600%) |
| Chave privada em formato bruto | 32 B | 2.400 B | +2.368 B (+7.400%) |
| Mensagem considerada no estabelecimento | 32 B (chave pública) | 1.088 B (ciphertext) | +1.056 B (+3.300%) |
| Segredo compartilhado | 32 B | 32 B | 0 B |

**Armazenamento — 1.000.000 de chaves:** para chaves públicas, X25519 ocupa 32.000.000 B (32 MB) e ML-KEM-768 ocupa 1.184.000.000 B (1,184 GB), acréscimo de 1.152.000.000 B. Para chaves privadas brutas, os valores são 32.000.000 B e 2.400.000.000 B, acréscimo de 2.368.000.000 B. Os cálculos estão em `data/storage_scenario.csv`.\n\n**Comunicação — 1.000.000 de estabelecimentos:** considera-se uma chave pública X25519 de 32 B ou um ciphertext ML-KEM-768 de 1.088 B por estabelecimento. Os volumes são 32.000.000 B e 1.088.000.000 B, respectivamente, com acréscimo de 1.056.000.000 B (1,056 GB decimais).

O cenário considera somente esses elementos; não inclui cabeçalhos, certificados, retransmissões ou outras mensagens do protocolo. Os valores reproduzíveis estão em `data/communication_scenario.csv`.

## 6. Processamento, recursos e reprodutibilidade

O script `src/benchmark_pqc.py` mede 30 repetições e preserva os tempos brutos no JSON, além das medianas. ML-KEM-768 registra KeyGen, Encaps e Decaps separadamente; em todas as repetições, os segredos de encapsulamento e desencapsulamento coincidiram. X25519 registra a geração de um par de chaves e duas operações de exchange.

| Operação | Mediana (ms) |
|---|---:|
| X25519 KeyGen de um par | 0,063249 |
| X25519 duas operações exchange | 0,063679 |
| ML-KEM-768 KeyGen + exportação da chave pública | 6,968748 |
| ML-KEM-768 Encaps | 3,388151 |
| ML-KEM-768 Decaps | 3,072942 |

**Ressalva metodológica:** X25519 é medido pela biblioteca Python `cryptography`, enquanto ML-KEM-768 é medido pela interface de linha de comando do OpenSSL. Os tempos incluem overheads diferentes de interfaces, processos e arquivos, portanto não isolam o custo intrínseco das primitivas. Os tamanhos PEM observados pelo OpenSSL também não devem ser confundidos com os tamanhos normativos da seção 4.

O benchmark registra CPU e pico de memória agregados do processo e dos subprocessos OpenSSL. Nesta execução, o pico de RSS do processo foi 28.164 KiB; o consumo de CPU foi 0,070544 s de usuário e 0,016358 s de sistema no processo principal. Esses valores não são medidos por operação. Energia não foi medida. O resumo do ambiente está em `data/environment.txt`, e as amostras brutas em `data/benchmark_pqc.json`.

## 7. Impactos e estratégia de migração

A migração exige mais do que trocar uma primitiva. É necessário atualizar bibliotecas e versões de protocolos, negociar suporte ao KEM, adaptar formatos e tamanhos de chaves e ciphertexts, revisar buffers e limites de mensagens/MTU, atualizar armazenamento e rotação de chaves e testar interoperabilidade. Em dispositivos IoT, devem ser medidos consumo de memória, CPU, energia e latência no hardware-alvo.

Uma implantação gradual pode considerar um modo híbrido, desde que utilize uma composição e um protocolo especificados e analisados. A troca de X25519 por ML-KEM não elimina a necessidade de autenticação e de assinaturas digitais resistentes a ataques quânticos quando aplicável.

## 8. Respostas ao enunciado

**Q1. Qual foi a maior instância comprometida experimentalmente?**  
C32_F23: corpo F23, curva y²=x³+x+10 (mod 23), P=(5,5), Q=(8,22), ordem 32 e d=3 recuperado. O circuito usa 15 qubits lógicos e 8 ancillas limpas na síntese V-chain (23 qubits transpilados), com 1.024 shots, profundidade 322.591, 417.102 operações e 138.292 CX.

**Q2. Qual foi o principal fator limitante?**  
O custo de sintetizar o oráculo reversível por tabela em portas elementares: a instância de ordem 32 chega a 138.292 CX e profundidade 322.591. O modelo não implementa aritmética de curva escalável e não inclui ruído nem conectividade de hardware físico.

**Q3. Por que X25519 é vulnerável a computadores quânticos suficientemente grandes?**  
Porque sua segurança está relacionada à dificuldade do ECDLP, para o qual Shor oferece um algoritmo quântico eficiente em um computador tolerante a falhas e suficientemente grande. A instância reduzida ilustra a estrutura matemática, não os recursos necessários para atacar Curve25519.

**Q4. Qual alternativa PQC é adequada?**  
ML-KEM-768, padronizado no NIST FIPS 203, mantém a função de estabelecimento de segredo compartilhado por encapsulamento. A autenticação e as assinaturas precisam ser tratadas separadamente.

**Q5. Qual é o custo quantitativo?**  
A chave pública passa de 32 B para 1.184 B; a chave privada bruta, de 32 B para 2.400 B; e a mensagem considerada, de 32 B para 1.088 B. Em um milhão de estabelecimentos, o acréscimo de comunicação é 1.056.000.000 B. Os tempos medianos de KeyGen, Encaps e Decaps estão na seção 5. CPU e pico de memória são registrados de forma agregada; energia não foi medida.

**Q6. Quais alterações seriam necessárias em um sistema real?**  
Atualizar bibliotecas, protocolos e negociação de algoritmos; adaptar formatos, buffers, armazenamento, rotação e limites de mensagens; planejar provisionamento e distribuição de chaves; e validar interoperabilidade e compatibilidade nos dispositivos.

**Q7. Basta substituir o algoritmo?**  
Não. A migração exige mudanças de protocolo e arquitetura, planejamento de provisionamento e armazenamento, tratamento de mensagens maiores, compatibilidade entre versões e avaliação de recursos dos dispositivos. Em alguns sistemas, pode ser necessária uma etapa híbrida durante a transição.

## 9. Conclusão

O circuito Qiskit/Aer recuperou d=3 nas quatro instâncias reduzidas de ECDLP, até a ordem 32. A síntese para a base {u, cx} permitiu medir profundidade, operações totais e portas CX. O experimento continua limitado por um oráculo de tabela clássica e por simulação ideal, não representando ataque a Curve25519 real. A comparação mostra aumento dos elementos de comunicação e armazenamento ao migrar para ML-KEM-768; os benchmarks funcionais, tempos brutos, CPU e pico de memória foram registrados com as ressalvas metodológicas descritas.

## Referências

1. IETF. **RFC 7748 — Elliptic Curves for Security**. 2016. https://www.rfc-editor.org/rfc/rfc7748
2. NIST. **FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard**. 2024. https://doi.org/10.6028/NIST.FIPS.203
3. Material da disciplina. **Avaliação Experimental de Algoritmos Criptográficos frente ao Algoritmo de Shor e Migração Pós-Quântica**. 2026.
