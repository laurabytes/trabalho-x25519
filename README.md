# Avaliação experimental do X25519 e migração para ML-KEM-768

Projeto de Computação Quântica e Defesa — 2026

## Conteúdo

- `relatorio_tecnico.docx` e `relatorio_tecnico.md`: relatório técnico.
- `src/toy_ecdlog.py`: experimento didático de ECDLP em curvas pequenas, com amostragem idealizada da etapa de Fourier e pós-processamento clássico.
- `src/benchmark_pqc.py`: benchmark funcional X25519 × ML-KEM-768 usando OpenSSL 3.5+ (quando o provedor/CLI oferece ML-KEM-768).
- `src/benchmark_sizes.py`: tabela reproduzível de tamanhos padronizados e cálculos de impacto.
- `data/`: dados de referência e resultados gerados localmente.
- `figures/`: gráficos do cenário quantitativo de comunicação.
- `requirements.txt`: dependências Python.

## Aviso metodológico importante

O experimento `toy_ecdlog.py` implementa uma **simulação idealizada de amostragem de Fourier para um ECDLP pequeno**, com pós-processamento clássico. Ele não é um circuito quântico reversível completo de Shor, não executa em Qiskit/Aer/FakeProvider e não quebra X25519/Curve25519. O relatório identifica essa limitação explicitamente. Não apresente esse resultado como quebra de chave real nem como execução de Shor em hardware quântico.

O experimento anterior de fatoração `N=77, a=30` é citado apenas como validação separada do fluxo de fatoração, não como ataque ao X25519.

## Requisitos

- Python 3.10+
- Para o experimento toy: `numpy`
- Para os gráficos: `matplotlib`
- Para o benchmark X25519: `cryptography`
- Para ML-KEM-768: OpenSSL 3.5 ou superior com suporte a ML-KEM-768 na instalação local.

Instalação:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução

### 1. Experimento toy ECDLP

```bash
python src/toy_ecdlog.py --output data/toy_ecdlog_results.json
```

O script:
1. constrói uma curva elíptica pequena sobre um corpo primo;
2. encontra um ponto gerador e sua ordem;
3. escolhe um escalar secreto de teste e calcula `Q = dP`;
4. calcula a distribuição idealizada de Fourier para a relação de período;
5. amostra resultados e tenta recuperar `d` por busca/classificação dos candidatos;
6. registra parâmetros, amostras, recuperação e limitações.

É uma demonstração conceitual do problema de subgrupo oculto, não um circuito Shor completo. Para a entrega estritamente experimental solicitada no enunciado, ainda é necessário implementar/decompor o circuito reversível de ECDLP no Qiskit/Aer e extrair profundidade e contagens de portas.

### 2. Benchmark X25519 e ML-KEM-768

```bash
python src/benchmark_pqc.py --repetitions 30 --output data/benchmark_pqc.json
```

O script executa X25519 por `cryptography` e tenta executar ML-KEM-768 via comandos OpenSSL. Se o OpenSSL local não oferecer os comandos/algoritmo necessários, registra a indisponibilidade sem inventar tempos.

### 3. Tamanhos e cenários

```bash
python src/benchmark_sizes.py
```

Gera `data/size_comparison.csv` e `figures/communication_1m.png`.

## Reprodutibilidade

Registre:
- versão do Python (`python --version`);
- versão do OpenSSL (`openssl version`);
- sistema operacional e processador;
- versões instaladas (`python -m pip freeze`);
- número de repetições e carga de execução.

Os tempos são dependentes do hardware e da implementação e devem ser coletados novamente na máquina de execução. Não compare tempos obtidos em máquinas diferentes como se fossem equivalentes.

## Estrutura

```text
trabalho-x25519/
├── README.md
├── requirements.txt
├── relatorio_tecnico.md
├── relatorio_tecnico.docx
├── src/
│   ├── toy_ecdlog.py
│   ├── benchmark_pqc.py
│   └── benchmark_sizes.py
├── data/
│   ├── tamanhos_padronizados.csv
│   └── (resultados gerados pelos scripts)
├── figures/
│   └── communication_1m.png
└── notebooks/
    └── roteiro_experimental.md
```

## Referências principais

- IETF. RFC 7748 — Elliptic Curves for Security. https://www.rfc-editor.org/rfc/rfc7748
- NIST. FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard. https://doi.org/10.6028/NIST.FIPS.203
- Shor, P. W. Algorithms for quantum computation: discrete logarithms and factoring. FOCS, 1994.
