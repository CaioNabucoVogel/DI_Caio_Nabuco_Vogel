"""
run_scylla.py

Submete os arquivos .py gerados por csv_to_py.py à plataforma Scylla, a ferramenta de
classificação de code smells desenvolvida internamente ao projeto de pesquisa (heurística
baseada em AST, aprendizado de máquina, aprendizado profundo e modelos de linguagem), e
normaliza as detecções de 'Long Method' e 'Long Parameter List' retornadas em um CSV
"largo", com uma linha por arquivo analisado.

Os diretórios de entrada e saída utilizados por este script são definidos internamente no
código-fonte, não havendo parâmetros de linha de comando para configurá-los.

Uso:
    python run_scylla.py
"""
import os
import sys
import glob
import pandas as pd
import uuid
from pathlib import Path

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Candidatos a caminho base onde 'src' pode estar
possible_paths = [
    os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "Scylla", "lm4smells-core", "lm4smells-code-extractor.API", "src")),
    os.path.abspath(os.path.join(CURRENT_DIR, "..", "Scylla", "lm4smells-core", "lm4smells-code-extractor.API", "src")),
    os.path.abspath(os.path.join(CURRENT_DIR, "Scylla", "lm4smells-core", "lm4smells-code-extractor.API", "src")),
]

SCYLLA_SRC = None
for path in possible_paths:
    if os.path.exists(path):
        SCYLLA_SRC = path
        break

if not SCYLLA_SRC:
    raise FileNotFoundError(
        f"Não foi possível encontrar o diretório 'src' do Scylla.\n"
        f"Caminhos testados:\n" + "\n".join(possible_paths)
    )

# 2. Adiciona a pasta 'src' E a pasta 'src/app' ao sys.path
SCYLLA_APP = os.path.join(SCYLLA_SRC, "app")

if SCYLLA_SRC not in sys.path:
    sys.path.insert(0, SCYLLA_SRC)

if os.path.exists(SCYLLA_APP) and SCYLLA_APP not in sys.path:
    sys.path.insert(0, SCYLLA_APP)

print(f"Diretório Scylla (src) importado: {SCYLLA_SRC}")
print(f"Diretório Scylla (app) importado: {SCYLLA_APP}")

# 3. Importação dinâmica e segura do módulo/classe de smells
try:
    import infrastructure.modules.smells.ast.smells as smells_module
except ModuleNotFoundError:
    import app.infrastructure.modules.smells.ast.smells as smells_module

# Identifica como chamar o analisador (classe ou módulo direto)
if hasattr(smells_module, "Smells"):
    analyzer = smells_module.Smells()
elif hasattr(smells_module, "ASTSmells"):
    analyzer = smells_module.ASTSmells()
elif hasattr(smells_module, "ASTSmellsAnalyzer"):
    analyzer = smells_module.ASTSmellsAnalyzer()
else:
    analyzer = smells_module  # Usa o módulo diretamente se as funções forem livres

# Configuração de Diretórios de Entrada e Saída
INPUT_DIR = "./saida"
OUTPUT_DIR = Path("resultados/scylla")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_RAW_CSV = OUTPUT_DIR / "scylla_raw.csv"
OUTPUT_PER_FILE_CSV = OUTPUT_DIR / "scylla_per_file.csv"

ALL_CATEGORIES = [
    "data_class",
    "large_class",
    "lazy_class",
    "long_method",
    "long_parameter_list",
    "magic_numbers"
]

# Apenas estes smells serão avaliados com 1 e 0
EVALUATED_CATEGORIES = ["long_method", "long_parameter_list"]

files_list = glob.glob(os.path.join(INPUT_DIR, "*.py"))
total_files = len(files_list)

raw_records = []
per_file_records = []

print(f"Iniciando análise direta em {total_files} arquivos...")

for index, file_path in enumerate(files_list, 1):
    filename = os.path.basename(file_path)
    print(f"[{index}/{total_files}] Analisando: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"   ↳ Erro ao ler arquivo: {e}")
        continue

    task_id = str(uuid.uuid4())
    found_smells = set()

    # --- 1. Análise de Long Parameter List ---
    if hasattr(analyzer, "long_parameter_list"):
        try:
            param_occurrences = analyzer.long_parameter_list(
                task_id=task_id,
                file_contents=content,
                file_names=filename
            )
            
            if param_occurrences:
                for occ in param_occurrences:
                    smell_val = occ.smell_type.value if hasattr(occ, 'smell_type') and hasattr(occ.smell_type, 'value') else str(occ)
                    raw_records.append({
                        "filename": filename,
                        "smell_type": smell_val,
                        "description": getattr(occ, 'description', '')
                    })
                    # Registra apenas se for o smell real (ignora prefixo "No ")
                    if "No Long Parameter List" not in smell_val and "No " not in getattr(occ, 'description', ''):
                        found_smells.add("long_parameter_list")

        except Exception as e:
            print(f"   ↳ Erro em long_parameter_list: {e}")

    # --- 2. Análise de Long Method ---
    if hasattr(analyzer, "long_method"):
        try:
            method_occurrences = analyzer.long_method(
                task_id=task_id,
                file_contents=content,
                file_names=filename
            )
            
            if method_occurrences:
                for occ in method_occurrences:
                    smell_val = occ.smell_type.value if hasattr(occ, 'smell_type') and hasattr(occ.smell_type, 'value') else str(occ)
                    raw_records.append({
                        "filename": filename,
                        "smell_type": smell_val,
                        "description": getattr(occ, 'description', '')
                    })
                    # Registra apenas se for o smell real (ignora prefixo "No ")
                    if "No Long Method" not in smell_val and "No " not in getattr(occ, 'description', ''):
                        found_smells.add("long_method")

        except Exception as e:
            print(f"   ↳ Erro em long_method: {e}")

    # --- 3. Monta a linha One-Hot Encoding com valores vazios para os não julgados ---
    file_row = {"generated_filename": filename}
    for cat in ALL_CATEGORIES:
        if cat in EVALUATED_CATEGORIES:
            file_row[f"scylla_{cat}"] = 1 if cat in found_smells else 0
        else:
            file_row[f"scylla_{cat}"] = ""  # Deixa vazio no CSV (ex: ,,)

    per_file_records.append(file_row)

print("\nGerando arquivos CSV...")

# Exporta CSV Bruto
df_raw = pd.DataFrame(raw_records)
df_raw.to_csv(OUTPUT_RAW_CSV, index=False)
print(f"Relatório bruto salvo em: {OUTPUT_RAW_CSV}")

# Exporta CSV Final
df_per_file = pd.DataFrame(per_file_records)
if not df_per_file.empty:
    df_per_file.sort_values(by="generated_filename", inplace=True)
df_per_file.to_csv(OUTPUT_PER_FILE_CSV, index=False)

print(f"Dataset consolidado salvo em: {OUTPUT_PER_FILE_CSV}")