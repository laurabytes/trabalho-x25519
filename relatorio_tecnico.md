# Avaliação experimental do X25519 e migração para criptografia pós-quântica

**Disciplina:** Computação Quântica e Defesa  
**Tema:** X25519 e ML-KEM-768  
**Ano:** 2026  
**Integrantes:** ____________________________________  
**Professor(a):** ____________________________________

## Resumo

Este trabalho analisa o mecanismo de acordo de chaves X25519, cuja segurança clássica está associada ao problema do logaritmo discreto em curvas elípticas (ECDLP), e discute sua vulnerabilidade teórica ao algoritmo de Shor. A alternativa selecionada é ML-KEM-768, mecanismo de encapsulamento de chaves padronizado pelo NIST no FIPS 203. A comparação de tamanhos mostra aumento relevante de dados: a chave pública passa de 32 para 1.184 bytes e o ciphertext ML-KEM-768 possui 1.088 bytes. O relatório separa os resultados confirmados das medições ainda pendentes e não afirma que uma chave real X25519 tenha sido quebrada.

## 1. Introdução

X25519 é uma função de Diffie–Hellman em curva elíptica definida para Curve25519. É usada para que duas partes estabeleçam um segredo compartilhado sem transmiti-lo diretamente. O RFC 7748 define entradas e saídas de 32 bytes. A segurança clássica do mecanismo está relacionada à dificuldade do ECDLP.

O objetivo deste trabalho é explicar a relação entre X25519, ECDLP e Shor; estudar uma instância pequena; selecionar uma alternativa pós-quântica que preserve a função de acordo de chaves; e quantificar impactos de armazenamento, comunicação e processamento.

## 2. X25519 e o problema matemático

Sejam `a` e `b` os escalares privados das partes. As chaves públicas são derivadas de um ponto base e os dois lados calculam:

`A = X25519(a, base)`  
`B = X25519(b, base)`  
`K = X25519(a, B) = X25519(b, A)`

O problema matemático subjacente à segurança de sistemas de curva elíptica pode ser descrito como: dados um ponto `P` e `Q = dP`, recuperar o escalar `d`. Em grupos adequados, esse problema é considerado computacionalmente difícil para computadores clássicos.

O algoritmo de Shor resolve problemas de fatoração e logaritmo discreto em tempo polinomial no modelo de computador quântico tolerante a falhas. Portanto, um computador quântico suficientemente grande ameaça mecanismos ECC, incluindo X25519. Isso não significa que o hardware quântico atual consiga quebrar uma sessão X25519 real.

## 3. Experimento reduzido de ECDLP

O script `src/ecdlog_shor.py` implementa a estrutura de subgrupo oculto para quatro curvas curtas de Weierstrass sobre corpos primos pequenos, com ordens 4, 8, 16 e 32. Para cada caso, calcula `P`, `Q=3P` e a função `f(u,v)=[u]P+[v]Q` usando operações reais de pontos da curva. O oráculo associa cada resultado a um estado do registrador de pontos. Em seguida, o registrador de pontos é descartado por soma das probabilidades, aplica-se a QFT exata nos dois registradores de expoentes e amostram-se pares `(k_u,k_v)`. Quando `k_u` é invertível módulo `r`, recupera-se `d=k_v*k_u^{-1} mod r`.

A execução reproduzível padrão usa 4.096 shots e semente 20261110. As quatro instâncias recuperam `d=3`; a maior, C32_F23, usa 15 qubits lógicos no modelo de três registradores. A fração de pares que satisfaz a relação de período é 1 no modelo ideal. A fração de amostras informativas aproxima `phi(r)/r=0,5` para ordens potências de dois.

**Limitação essencial:** trata-se de simulação ideal de estado vetorial em NumPy, com oráculo por tabela de pontos e QFT aplicada como matriz exata. Não é um circuito nativo transpilado em Qiskit/Aer/FakeProvider, não modela ruído ou conectividade e não recupera uma chave Curve25519 real. As métricas de qubits são do modelo lógico reduzido; não representam recursos de hardware.

Em experimentos anteriores do ambiente, foi testada separadamente a fatoração de `N=77`, com base `a=30`. A execução ideal com 1.024 shots encontrou período `r=30` e fatores `7` e `11`; uma execução com 8 shots não recuperou o resultado. Esses resultados validam apenas parte do fluxo de fatoração e **não** são uma instância de ECDLP nem um ataque a X25519.

| Experimento conhecido | Configuração | Resultado | Interpretação |
|---|---|---|---|
| Fatoração ideal | N=77, a=30, 1.024 shots | período 30; fatores 7 e 11 | teste de fatoração reduzida |
| Fatoração com poucos shots | N=77, a=30, 8 shots | solução não recuperada | amostragem insuficiente |
| ECDLP para X25519 | curva reduzida toy | script reproduzível incluído | modelo idealizado, não circuito Shor completo |

As métricas de qubits, profundidade, gates totais e gates de dois qubits não são informadas para o toy porque não existe circuito quântico executado. Para atender integralmente à parte de Shor do enunciado, é necessário implementar o circuito reversível de ECDLP no Qiskit/Aer, transpilar para um backend definido e registrar essas métricas.

## 4. Comparação com parâmetros reais

X25519 usa Curve25519 e codificações de 32 bytes. A instância toy tem campo e subgrupo muito menores e não é comparável em segurança à curva real. Uma execução em escala real exigiria muitos qubits lógicos, correção de erros, alta fidelidade de portas, conectividade apropriada e circuitos profundos. O número de qubits físicos necessários seria maior que o número lógico.

A vulnerabilidade é algorítmica: Shor é capaz de resolver o logaritmo discreto em grupos abelianos no modelo quântico adequado. A demonstração em pequena escala ilustra a estrutura matemática, mas não demonstra capacidade atual de quebrar chaves reais.

## 5. Alternativa pós-quântica: ML-KEM-768

Como X25519 realiza acordo de chaves, a alternativa deve realizar a mesma função. ML-KEM-768 é um mecanismo de encapsulamento de chaves baseado em reticulados (Module-LWE), padronizado pelo NIST no FIPS 203. Não é algoritmo de assinatura digital.

Seu fluxo é:
1. **KeyGen:** gera chave pública e chave privada de desencapsulamento.
2. **Encaps:** usa a chave pública para gerar ciphertext e segredo compartilhado.
3. **Decaps:** usa a chave privada e o ciphertext para recuperar o segredo.

A seleção de ML-KEM-768 preserva a finalidade de estabelecimento de segredo compartilhado e utiliza um padrão pós-quântico publicado pelo NIST.

## 6. Comparação quantitativa de tamanhos

Os tamanhos abaixo são parâmetros padronizados. Para X25519, considera-se a chave pública de 32 bytes e o escalar privado bruto de 32 bytes. Para ML-KEM-768, os tamanhos do FIPS 203 são 1.184 bytes para chave pública, 2.400 bytes para chave privada de desencapsulamento, 1.088 bytes para ciphertext e 32 bytes para segredo compartilhado.

| Métrica | X25519 | ML-KEM-768 | Diferença |
|---|---:|---:|---:|
| Chave pública | 32 B | 1.184 B | +1.152 B (+3.600%) |
| Chave privada bruta | 32 B | 2.400 B | +2.368 B (+7.400%) |
| Mensagem considerada na troca | 32 B | 1.088 B | +1.056 B (+3.300%) |
| Segredo compartilhado | 32 B | 32 B | 0 B |

Os formatos internos de chave privada e o armazenamento em aplicações podem acrescentar metadados e codificação. A tabela compara os tamanhos brutos definidos para os elementos criptográficos, não certificados ou arquivos PEM completos.

### Cenário de comunicação

Considerando, de forma simplificada, uma mensagem de 32 bytes por sessão para X25519 e um ciphertext de 1.088 bytes por sessão para ML-KEM-768:

- 1.000.000 × 64 B = 64.000.000 bytes (64 MB), considerando duas shares públicas X25519;
- 1.000.000 × 1.088 B + 1.184 B de chave pública provisionada = 1.088.001.184 bytes;
- diferença = 1.024.001.184 bytes (aproximadamente 1,024 GB).

Esse cenário compara apenas os elementos indicados e não inclui cabeçalhos, certificados, retransmissões ou outras mensagens do protocolo. O custo exato depende do protocolo e do modo de integração.

## 7. Impactos da migração

### 7.1 Armazenamento

A chave pública ML-KEM-768 é 37 vezes maior que a chave pública X25519 (1.184 B contra 32 B). A chave privada bruta indicada é 75 vezes maior (2.400 B contra 32 B). No cenário de troca, são comparadas duas shares públicas X25519 (64 B) com um ciphertext ML-KEM-768 (1.088 B). Em dispositivos IoT com flash e RAM limitadas, deve-se avaliar armazenamento persistente, buffers temporários, cópias de chaves e memória de execução.

### 7.2 Comunicação

O ciphertext ML-KEM-768 possui 1.088 bytes. No cenário de um milhão de sessões, o volume é 64 MB para X25519 e 1.088.001.184 bytes para ML-KEM-768 com uma chave pública provisionada uma vez. Em redes de baixa largura de banda, enlaces intermitentes ou dispositivos com franquia de transmissão limitada, o aumento pode afetar latência, energia de rádio e custo de comunicação.

### 7.3 Processamento

O processamento deve ser comparado por operação: KeyGen, Encaps e Decaps. O benchmark fornecido mede X25519 em Python e verifica se a instalação OpenSSL local anuncia ML-KEM-768. O script executa KeyGen, Encaps e Decaps via OpenSSL CLI quando o build oferece ML-KEM-768. Em cada repetição, compara os segredos encapsulado e desencapsulado byte a byte. Os tempos incluem overhead de subprocesso e I/O e são específicos do ambiente.

Tempos de CLI ou Python incluem overhead de inicialização e wrappers; não devem ser tratados como benchmark puro sem qualificação. Para IoT, também é importante medir pico de RAM, CPU, energia e latência de comunicação.

## 8. Estratégia de migração e arquitetura

A migração não consiste apenas em trocar uma primitiva. É necessário:

- atualizar bibliotecas criptográficas e validar versões com suporte a ML-KEM;
- atualizar protocolos e negociar capacidades entre clientes e servidores;
- adaptar formatos, serialização, armazenamento e rotação de chaves;
- revisar tamanhos máximos de mensagens, buffers, MTU, fragmentação e timeouts;
- testar interoperabilidade e comportamento em falhas;
- planejar implantação gradual e, quando apropriado, um modo híbrido durante a transição;
- inventariar dependências criptográficas e identificar dados que precisam de confidencialidade de longo prazo;
- avaliar memória, processamento, energia e largura de banda em dispositivos restritos.

Certificados digitais e assinaturas não são substituídos por ML-KEM: para assinatura pós-quântica, a família adequada inclui ML-DSA. A arquitetura deve separar acordo de chaves, assinatura/autenticação e derivação de chaves.

## 9. Respostas às questões do enunciado

**Q1. Qual foi a maior instância comprometida experimentalmente utilizando Shor?**  
A maior instância reduzida de ECDLP foi C32_F23, com curva `y²=x³+x+10 mod 23`, ponto `P=(5,5)`, `Q=(8,22)`, ordem 32, segredo de teste `d=3`, 15 qubits lógicos e 4.096 shots. A simulação ideal recupera `d=3`. Isso não é uma chave Curve25519 real nem uma execução em hardware.

**Q2. Qual foi o principal fator limitante?**  
O simulador de estado vetorial cresce exponencialmente com o número de qubits. Além disso, o oráculo por tabela de pontos não é uma implementação escalável da aritmética reversível de Curve25519. A simulação não inclui decomposição nativa, conectividade ou ruído.

**Q3. Por que X25519 é vulnerável mesmo sem quebra da chave real?**  
Porque sua segurança depende do ECDLP, que Shor resolve eficientemente em um computador quântico tolerante a falhas e suficientemente grande. A ausência de quebra experimental hoje decorre das limitações de escala e confiabilidade do hardware, não de resistência matemática ao algoritmo.

**Q4. Qual alternativa PQC é adequada?**  
ML-KEM-768, porque X25519 é usado para estabelecimento de chaves e ML-KEM é um mecanismo de encapsulamento de chaves padronizado no NIST FIPS 203. ML-DSA é voltado a assinaturas e não é substituto direto de X25519.

**Q5. Qual é o custo quantitativo da migração?**  
A chave pública passa de 32 para 1.184 bytes (+1.152 bytes); a chave privada bruta, de 32 para 2.400 bytes (+2.368 bytes); o elemento de mensagem comparado, de 32 para 1.088 bytes (+1.056 bytes). Em um milhão de sessões, isso representa cerca de 1,056 GB adicionais no cenário simplificado. O segredo compartilhado permanece em 32 bytes. Os tempos de processamento devem ser medidos na implementação local.

**Q6. Quais alterações seriam necessárias?**  
Atualização de bibliotecas, protocolos, negociação de capacidades, formatos e armazenamento de chaves, buffers, limites de mensagens, gestão de chaves, testes de interoperabilidade e implantação gradual. Certificados e assinaturas exigem análise separada porque ML-KEM não é assinatura digital.

**Q7. A simples substituição do algoritmo é suficiente?**  
Não. A mudança afeta formatos, tamanhos de mensagens, buffers, protocolos, desempenho, consumo de memória e energia. É necessário revisar a arquitetura, testar compatibilidade ponta a ponta e considerar implantação híbrida temporária quando adequada.

## 10. Conclusão

X25519 é vulnerável em princípio a um computador quântico tolerante a falhas que execute Shor em escala suficiente, pois depende do ECDLP. O experimento de estado vetorial incluído recupera o escalar de teste em quatro instâncias pequenas, mas não equivale a uma execução nativa de circuito Shor nem à quebra de Curve25519. A migração para ML-KEM-768 mantém a função de estabelecimento de chaves e oferece uma alternativa padronizada, mas aumenta significativamente os tamanhos de chaves e mensagens. A adoção exige mudanças de software, protocolo e arquitetura, além de medições locais de desempenho e recursos.

## Referências

1. IETF. **RFC 7748: Elliptic Curves for Security**. 2016. https://www.rfc-editor.org/rfc/rfc7748
2. NIST. **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard**. 2024. https://doi.org/10.6028/NIST.FIPS.203
3. Shor, P. W. **Algorithms for quantum computation: discrete logarithms and factoring**. Proceedings of the 35th Annual Symposium on Foundations of Computer Science, 1994.
4. Material da disciplina. **Exercício – Avaliação Experimental de Algoritmos Criptográficos frente ao Algoritmo de Shor e Migração Pós-Quântica**. 2026.
