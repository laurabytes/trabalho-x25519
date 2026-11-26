# trabalho: x25519 e migração pós-quântica

**disciplina:** computação quântica e defesa  
**tema:** x25519, ecdlp, algoritmo de shor e ml-kem-768  
**integrantes:** ______________________________________

## resumo

neste trabalho, estudamos por que o x25519 pode ser afetado pelo algoritmo de shor e testamos o ml-kem-768 como alternativa pós-quântica. a parte experimental implementa instâncias reduzidas de ecdlp em circuito qiskit, transpila o oráculo reversível para a base de portas {u, cx} e executa a versão compacta no aersimulator. foram avaliadas quatro ordens (4, 8, 16 e 32), recuperando d=3 em todas. a maior instância utilizou 15 qubits lógicos, 8 ancillas na síntese, 1.024 shots, profundidade 322.591 e 138.292 portas cx. o benchmark funcional x25519/ml-kem-768 foi repetido 30 vezes, preservando amostras brutas, medianas e recursos agregados. o teste usa curvas pequenas. ele não quebra a curve25519 real.

## 1. introdução e problema matemático

x25519 é um mecanismo de acordo de chaves baseado na curva curve25519. duas partes geram valores privados, calculam chaves públicas e combinam o segredo local com a chave pública remota para obter o mesmo segredo compartilhado. o rfc 7748 define entradas e saídas de 32 bytes.

a segurança clássica está relacionada ao problema do logaritmo discreto em curvas elípticas (ecdlp): dados um ponto base p e um ponto público q=[d]p, recuperar o escalar privado d. o algoritmo de shor resolve o logaritmo discreto em grupos abelianos em tempo polinomial no modelo de computador quântico tolerante a falhas. isso representa uma ameaça matemática a mecanismos ecc, mas não significa que computadores quânticos atuais consigam quebrar uma chave x25519 real.

## 2. experimento reduzido de ecdlp com shor em qiskit/aer

o experimento principal está implementado em `src/ecdlog_qiskit.py`. o circuito prepara dois registradores de fase em superposição, calcula reversivelmente a função de grupo f(u,v)=[u]p+[v]q por um oráculo de consulta em tabela, aplica a qft inversa e mede os registradores. o pós-processamento clássico usa as amostras de fourier para recuperar o escalar de teste.

o oráculo é reversível e implementado com portas multi-controladas x. para medir recursos em uma base elementar, uma cópia equivalente usa ancillas limpas na síntese v-chain e é transpilada para {u, cx}. a execução ideal das medições é feita no aersimulator com a versão compacta equivalente do circuito. a síntese de métricas usa optimization_level=0; a execução no simulador usa optimization_level=1. ambiente: qiskit 1.4.6 e qiskit aer 0.17.2.

| instância | p (bits) | ordem r (bits) | p | q | qubits lógicos | qubits transpilados | profundidade | operações totais | cx | shots | tempo total (s) | p(correta/shot) | d recuperado |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| c4_f5 | 5 (3) | 4 (2) | (1,2) | (1,3) | 6 | 8 | 679 | 892 | 298 | 1.024 | 0,078 | 48,44% | 3 |
| c8_f5 | 5 (3) | 8 (3) | (0,1) | (1,4) | 9 | 13 | 6.733 | 8.742 | 2.898 | 1.024 | 0,177 | 49,51% | 3 |
| c16_f11 | 11 (4) | 16 (4) | (0,1) | (8,1) | 12 | 18 | 50.199 | 64.992 | 21.540 | 1.024 | 0,722 | 50,00% | 3 |
| c32_f23 | 23 (5) | 32 (5) | (5,5) | (8,22) | 15 | 23 | 322.591 | 417.102 | 138.292 | 1.024 | 4,281 | 52,44% | 3 |

em todas as quatro instâncias, a fração observada de amostras que satisfaz a relação de período foi 1,0 e o escalar d=3 foi recuperado. a probabilidade empírica de uma medição individual ser informativa e produzir o candidato correto variou de 48,44% a 52,44%; a recuperação final utiliza 1.024 shots. os tamanhos de p e da ordem r em bits estão indicados entre parênteses na tabela. as contagens por par medido estão em `data/ecdlog_qiskit_measurements.csv`; os resultados completos em `data/ecdlog_qiskit_results.json`; e a tabela de métricas em `data/ecdlog_qiskit_metrics.csv`.

### maior instância

a maior instância resolvida foi c32_f23:

- corpo f23; curva y² = x³ + x + 10 (mod 23).
- p=(5,5), q=(8,22), ordem de p igual a 32.
- escalar conhecido e recuperado: d=3.
- dois registradores de fase com 5 qubits cada e registrador de ponto com 5 qubits.
- 15 qubits lógicos, mais 8 ancillas limpas na síntese v-chain (23 qubits transpilados).
- 1.024 shots; profundidade 322.591; 417.102 operações totais, incluindo 138.292 cx; probabilidade empírica de candidato correto por shot: 52,44%.
- tempo de construção dos circuitos: 0,505 s; transpilação de métricas: 1,668 s; transpilação do circuito compacto para aer: 0,127 s; simulação: 0,163 s; tempo total medido: 4,281 s.

### limitações experimentais

o oráculo usa uma tabela clássica de pontos e não implementa aritmética reversível escalável de curvas elípticas. a execução é ideal no aersimulator: não modela ruído, conectividade/calibração de um backend físico nem execução em qpu. assim, as métricas são da síntese do oráculo reduzido para {u, cx}, não uma estimativa de recursos para quebrar curve25519 real. também deixamos a simulação numpy como referência para conferir os resultados em `src/ecdlog_shor.py`.

a fatoração anterior de n=77, com a=30, valida parte do fluxo de shor, mas não é um ataque ao x25519 e não é contabilizada como resultado ecdlp neste trabalho.

## 3. comparação com parâmetros reais

o x25519 real opera sobre curve25519, definida sobre um campo de 255 bits, e oferece aproximadamente 128 bits de segurança clássica. a maior instância deste experimento usa p=23 (5 bits) e ordem de subgrupo r=32 (5 bits). portanto, o modelo reduzido é muito menor e serve para observar a estrutura matemática, não para estimar diretamente o custo de quebrar curve25519.

os qubits lógicos representam os registradores do algoritmo reduzido. os 23 qubits transpilados da maior instância incluem 8 ancillas para decompor o oráculo; não são uma estimativa de qubits físicos para um ataque real. uma execução em escala real exigiria correção quântica de erros, muitos qubits físicos por qubit lógico, fidelidade alta de portas, controle de decoerência, conectividade adequada e circuitos aritméticos muito mais complexos.

## 4. alternativa pós-quântica: ml-kem-768

ml-kem-768 é um mecanismo de encapsulamento de chaves baseado em reticulados, padronizado pelo nist no fips 203. seu fluxo é:

1. **keygen:** gera a chave pública e a chave de desencapsulamento.
2. **encaps:** usa a chave pública para produzir um ciphertext e um segredo compartilhado.
3. **decaps:** usa a chave privada e o ciphertext para recuperar o mesmo segredo.

ml-kem é um kem, não um algoritmo de assinatura digital. a migração de x25519 para ml-kem não substitui, por si só, os mecanismos de autenticação e assinatura do protocolo.

## 5. comparação quantitativa de tamanhos, armazenamento e comunicação

a tabela utiliza tamanhos normativos dos elementos criptográficos, não arquivos pem exportados pelo openssl.

| métrica | x25519 | ml-kem-768 | diferença |
|---|---:|---:|---:|
| chave pública | 32 b | 1.184 b | +1.152 b (+3.600%) |
| chave privada em formato bruto | 32 b | 2.400 b | +2.368 b (+7.400%) |
| mensagem considerada no estabelecimento | 32 b (chave pública) | 1.088 b (ciphertext) | +1.056 b (+3.300%) |
| segredo compartilhado | 32 b | 32 b | 0 b |

**armazenamento — 1.000.000 de chaves:** para chaves públicas, x25519 ocupa 32.000.000 b (32 mb) e ml-kem-768 ocupa 1.184.000.000 b (1,184 gb), acréscimo de 1.152.000.000 b. para chaves privadas brutas, os valores são 32.000.000 b e 2.400.000.000 b, acréscimo de 2.368.000.000 b. os cálculos estão em `data/storage_scenario.csv`.

**comunicação — 1.000.000 de estabelecimentos:** considera-se uma chave pública x25519 de 32 b ou um ciphertext ml-kem-768 de 1.088 b por estabelecimento. os volumes são 32.000.000 b e 1.088.000.000 b, respectivamente, com acréscimo de 1.056.000.000 b (1,056 gb decimais).

o cenário considera somente esses elementos; não inclui cabeçalhos, certificados, retransmissões ou outras mensagens do protocolo. os valores reproduzíveis estão em `data/communication_scenario.csv`.

## 6. processamento, recursos e reprodutibilidade

o script `src/benchmark_pqc.py` mede 30 repetições e preserva os tempos brutos no json, além das medianas. ml-kem-768 registra keygen, encaps e decaps separadamente; em todas as repetições, os segredos de encapsulamento e desencapsulamento coincidiram. x25519 registra a geração de um par de chaves e duas operações de exchange.

| operação | mediana (ms) |
|---|---:|
| x25519 keygen de um par | 0,062729 |
| x25519 duas operações exchange | 0,063765 |
| ml-kem-768 keygen + exportação da chave pública | 6,813892 |
| ml-kem-768 encaps | 3,343627 |
| ml-kem-768 decaps | 2,984659 |

**ressalva metodológica:** x25519 é medido pela biblioteca python `cryptography`, enquanto ml-kem-768 é medido pela interface de linha de comando do openssl. os tempos incluem overheads diferentes de interfaces, processos e arquivos, portanto não isolam o custo intrínseco das primitivas. os tamanhos pem observados pelo openssl também não devem ser confundidos com os tamanhos normativos da seção 4.

o benchmark registra cpu e pico de memória agregados do processo e dos subprocessos openssl. nesta execução, o pico de rss do processo foi 28.168 kib; o consumo de cpu foi 0,054513 s de usuário e 0,029437 s de sistema no processo principal. esses valores não são medidos por operação. energia não foi medida. o resumo do ambiente está em `data/environment.txt`, e as amostras brutas em `data/benchmark_pqc.json`.

## 7. impactos e estratégia de migração

a migração exige mais do que trocar uma primitiva. é necessário atualizar bibliotecas e versões de protocolos, negociar suporte ao kem, adaptar formatos e tamanhos de chaves e ciphertexts, revisar buffers e limites de mensagens/mtu, atualizar armazenamento e rotação de chaves e testar interoperabilidade. em dispositivos iot, devem ser medidos consumo de memória, cpu, energia e latência no hardware-alvo.

uma implantação gradual pode considerar um modo híbrido, desde que utilize uma composição e um protocolo especificados e analisados. a troca de x25519 por ml-kem não elimina a necessidade de autenticação e de assinaturas digitais resistentes a ataques quânticos quando aplicável.

## 8. respostas ao enunciado

**q1. qual foi a maior instância comprometida experimentalmente?**  
c32_f23: corpo f23, curva y²=x³+x+10 (mod 23), p=(5,5), q=(8,22), ordem 32 e d=3 recuperado. o circuito usa 15 qubits lógicos e 8 ancillas limpas na síntese v-chain (23 qubits transpilados), com 1.024 shots, profundidade 322.591, 417.102 operações e 138.292 cx.

**q2. qual foi o principal fator limitante?**  
o custo de sintetizar o oráculo reversível por tabela em portas elementares: a instância de ordem 32 chega a 138.292 cx e profundidade 322.591. o modelo não implementa aritmética de curva escalável e não inclui ruído nem conectividade de hardware físico.

**q3. por que x25519 é vulnerável a computadores quânticos suficientemente grandes?**  
porque sua segurança está relacionada à dificuldade do ecdlp, para o qual shor oferece um algoritmo quântico eficiente em um computador tolerante a falhas e suficientemente grande. a instância reduzida ilustra a estrutura matemática, não os recursos necessários para atacar curve25519.

**q4. qual alternativa pqc é adequada?**  
ml-kem-768, padronizado no nist fips 203, mantém a função de estabelecimento de segredo compartilhado por encapsulamento. a autenticação e as assinaturas precisam ser tratadas separadamente.

**q5. qual é o custo quantitativo?**  
para 1 milhão de chaves públicas, o acréscimo de armazenamento é 1,152 gb; para chaves privadas brutas, 2,368 gb. em 1 milhão de estabelecimentos, o acréscimo de comunicação é 1,056 gb. os tempos medianos de keygen, encaps e decaps estão na seção 6. cpu e pico de memória são registrados de forma agregada; energia não foi medida.

**q6. quais alterações seriam necessárias em um sistema real?**  
atualizar bibliotecas, protocolos e negociação de algoritmos; adaptar formatos, buffers, armazenamento, rotação e limites de mensagens; planejar provisionamento e distribuição de chaves; e validar interoperabilidade e compatibilidade nos dispositivos.

**q7. basta substituir o algoritmo?**  
não. a migração exige mudanças de protocolo e arquitetura, planejamento de provisionamento e armazenamento, tratamento de mensagens maiores, compatibilidade entre versões e avaliação de recursos dos dispositivos. em alguns sistemas, pode ser necessária uma etapa híbrida durante a transição.

## 9. conclusão

o circuito qiskit/aer recuperou d=3 nas quatro instâncias reduzidas de ecdlp, até a ordem 32. a síntese para a base {u, cx} permitiu medir profundidade, operações totais e portas cx. o experimento continua limitado por um oráculo de tabela clássica e por simulação ideal, não representando ataque a curve25519 real. a comparação mostra aumento dos elementos de comunicação e armazenamento ao migrar para ml-kem-768; os benchmarks funcionais, tempos brutos, cpu e pico de memória foram registrados com as ressalvas metodológicas descritas.

## referências

1. ietf. **rfc 7748 — elliptic curves for security**. 2016. https://www.rfc-editor.org/rfc/rfc7748
2. nist. **fips 203 — module-lattice-based key-encapsulation mechanism standard**. 2024. https://doi.org/10.6028/nist.fips.203
3. material da disciplina. **avaliação experimental de algoritmos criptográficos frente ao algoritmo de shor e migração pós-quântica**. 2026.
