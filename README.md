# Avaliação Comparativa de Ferramentas de Detecção de Code Smells em Python

Projeto de Iniciação Científica (PIBIC 2025-2026) que realiza uma avaliação comparativa
entre quatro ferramentas de detecção de code smells em Python — **Scylla**, **DPy**,
**PyExamine** e **SonarQube** — utilizando como base o dataset rotulado manualmente
[pyhub-smell](https://zenodo.org/records/21420951).

- **Aluno:** Caio Nabuco Vogel
- **Orientadora:** Profa. Juliana Alves Pereira
- **Departamento de Informática — PUC-Rio**

---

## Visão geral

O objetivo do projeto é comparar, de forma sistemática, o quanto cada ferramenta
concorda entre si e com o julgamento de especialistas na detecção de dois code smells
suportados simultaneamente por todas elas: **Long Method** e **Long Parameter List**.
Para isso, são calculadas métricas de concordância (Cohen's Kappa, Percentage Agreement)
e de classificação (Precision, Recall, F1-Score) tomando a rotulação manual do dataset
como *ground truth*.

O relatório completo com a metodologia, os resultados e a discussão está disponível
separadamente (Annual Activity Report, PIBIC 2025-2026).

---

## Estrutura do repositório

```
.
├── CSVs/                          # Subconjunto original do dataset pyhub-smell
│                                   # (arquivos "zeroshot" e "without_ast")
├── saida/                         # Arquivos .py gerados a partir dos CSVs (um por instância)
├── resultados/                    # CSVs de saída de cada ferramenta + ground truth
│   ├── dpy/
│   ├── pyexamine/
│   ├── sonarqube/
│   └── experts_ground_truth.csv
├── csv_to_py.py
├── run_dpy.py
├── run_pyexamine.py
├── run_scylla.py
├── run_sonarqube.py
├── build_experts_csv.py
├── DI_Caio_Nabuco_Vogel.ipynb     # Notebook de análise: métricas e gráficos/tabelas finais
└── code_quality_config.yaml       # Configuração usada na execução das análises
```

> **Observação:** este repositório contém apenas os artefatos autorais do projeto.
> As ferramentas de terceiros avaliadas (DPy, PyExamine, Scylla, SonarQube/SonarScanner)
> **não estão incluídas** e precisam ser obtidas e configuradas separadamente — veja a
> seção [Dependências externas](#dependências-externas).

---

## Workflow

O pipeline experimental segue quatro etapas, executadas nesta ordem:

```
CSVs/ ──► csv_to_py.py ──► saida/ ──► run_dpy.py       ──► resultados/dpy/
                                   ├─► run_pyexamine.py ──► resultados/pyexamine/
                                   ├─► run_scylla.py     ──► resultados/scylla/
                                   └─► run_sonarqube.py  ──► resultados/sonarqube/

CSVs/ ──► build_experts_csv.py ──► resultados/experts_ground_truth.csv

resultados/dpy/dpy_per_file.csv            ┐
resultados/pyexamine/pyexamine_per_file.csv│
resultados/scylla/scylla_per_file.csv      ├─► DI_Caio_Nabuco_Vogel.ipynb ──► métricas + gráficos/tabelas
resultados/sonarqube/sonar_per_file.csv    │
resultados/experts_ground_truth.csv        ┘
```

### 1. `csv_to_py.py` — preparação do dataset

Lê os CSVs filtrados do pyhub-smell (colunas `id`, `smell_type`, `file_name`, `code`,
`expert`, entre outras) e gera, para cada linha, um arquivo `.py` individual em `saida/`
contendo o código da coluna `code`. O nome do arquivo gerado segue o padrão:

```
{file_name}_{created_at}__{sufixo_expert}.py
```

onde `{sufixo_expert}` é uma sequência de 6 dígitos binários representando a rotulação dos
especialistas para `[data_class, large_class, lazy_class, long_method,
long_parameter_list, magic_numbers]`.

```bash
python csv_to_py.py --input-dir ./CSVs --output-dir ./saida
```

### 2. Execução das ferramentas

Cada script roda uma ferramenta diferente sobre os arquivos gerados em `saida/` e
normaliza a saída em um CSV "largo" (uma linha por arquivo, com colunas binárias para
cada smell), pronto para comparação.

```bash
python run_dpy.py       --input-dir ./saida --output-dir ./resultados/dpy
python run_pyexamine.py --input-dir ./saida --output-dir ./resultados/pyexamine
python run_sonarqube.py --input-dir ./saida --output-dir ./resultados/sonarqube
python run_scylla.py
```

> `run_scylla.py` não recebe parâmetros de linha de comando — os diretórios de entrada e
> saída são definidos internamente no código-fonte.

### 3. `build_experts_csv.py` — construção do ground truth

Consolida os 6 CSVs originais com as avaliações dos especialistas em um único arquivo de
referência, `experts_ground_truth.csv`, usado para comparar cada ferramenta contra a
rotulação manual.

```bash
python build_experts_csv.py --input-dir ./CSVs --output-file ./resultados/experts_ground_truth.csv
```

Colunas de saída:
- `generated_filename`: nome sanitizado do arquivo gerado (`{file_name}_{created_at}.py`)
- `expert_data_class`
- `expert_large_class`
- `expert_lazy_class`
- `expert_long_method`
- `expert_long_parameter_list`
- `expert_magic_numbers`

### 4. `DI_Caio_Nabuco_Vogel.ipynb` — cálculo das métricas e geração dos gráficos

Notebook Jupyter que carrega os cinco CSVs "per_file" produzidos nas etapas anteriores
(`resultados/dpy/dpy_per_file.csv`, `resultados/pyexamine/pyexamine_per_file.csv`,
`resultados/scylla/scylla_per_file.csv`, `resultados/sonarqube/sonar_per_file.csv` e
`resultados/experts_ground_truth.csv`) e produz **todas** as métricas e figuras
apresentadas no relatório do projeto:

- Contagem bruta de detecções por ferramenta (Long Method, Long Parameter List e ambos)
- Coeficiente **Cohen's Kappa** entre cada par de ferramentas e a média por ferramenta
- Coeficiente **Cohen's Kappa** de cada ferramenta em relação aos especialistas
- **Percentage Agreement (Po)** entre ferramentas e entre cada ferramenta e os especialistas
- **Precision**, **Recall** e **F1-Score** de cada ferramenta em relação aos especialistas
  (usando `sklearn.metrics`, com `zero_division=0`)
- **Matrizes de confusão** (via `ConfusionMatrixDisplay`) de cada ferramenta em relação
  aos especialistas, para Long Method e para Long Parameter List

As tabelas e gráficos são renderizados com `matplotlib`/`seaborn` e exportados como
arquivos `.jpeg` (ex: `percentage_agreement_between_tools.jpeg`,
`percentage_agreement_with_experts.jpeg`, `f1_score.jpeg`, `precision_score.jpeg`,
`recall_score.jpeg`, além das figuras de matriz de confusão), que são as imagens
utilizadas diretamente no relatório.

**Como rodar:**

```bash
jupyter notebook DI_Caio_Nabuco_Vogel.ipynb
```

> O notebook espera encontrar os CSVs no caminho relativo
> `Relatório_Pibic_2026/Extrator_ArqPy/resultados/...`. Se você mover o notebook para a
> raiz do repositório, ajuste esses caminhos na segunda célula antes de rodar.

---

## Dependências externas

As ferramentas avaliadas não fazem parte deste repositório e devem ser obtidas
separadamente:

| Ferramenta | Referência |
|---|---|
| Scylla | Oliveira et al., SBES 2025 |
| DPy | Bolouri & Sharma, MSR 2025 — [repositório](https://github.com) |
| PyExamine | Shivashankar & Martini, arXiv 2025 — [python_smells_detector](https://github.com/KarthikShivasankar/python_smells_detector) |
| SonarQube / SonarScanner | [docs.sonarsource.com](https://docs.sonarsource.com/sonarqube/) |

O dataset original **pyhub-smell** (rotulação completa) está disponível em:
https://zenodo.org/records/21420951

---

## Requisitos

- Python 3.x
- Para `DI_Caio_Nabuco_Vogel.ipynb`: `pandas`, `numpy`, `matplotlib`, `seaborn`,
  `scikit-learn`, `jupyter`
  ```bash
  pip install pandas numpy matplotlib seaborn scikit-learn jupyter
  ```
- Dependências específicas de cada script de execução (ver imports em cada arquivo)
- Acesso configurado às ferramentas listadas em [Dependências externas](#dependências-externas)

---

## Referências

1. OLIVEIRA, Igor et al. Code smell classification in Python: are small language models
   up to the task? SBES 2025.
2. BOLOORI, Aryan; SHARMA, Tushar. DPy: code smells detection tool for Python. MSR 2025.
3. SHIVASHANKAR, Karthik; MARTINI, Antonio. PyExamine: a comprehensive, un-opinionated
   smell detection tool for Python. arXiv, 2025.
4. OLIVEIRA, Igor Santos de et al. A Multi-Approach Evaluation of Python Code Smell
   Detection Using Heuristics, Learning Models, and Language Models. SBES 2026.
