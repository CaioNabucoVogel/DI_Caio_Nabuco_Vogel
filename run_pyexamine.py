"""
run_pyexamine.py

Executa o PyExamine (projeto local clonado em 'python_smells_detector') sobre os arquivos
.py gerados por csv_to_py.py, extraindo as detecções dos smells 'Long Method' e
'Long Parameter List'.

Os resultados retornados pela ferramenta são normalizados para um CSV "largo", pronto para
análise: uma linha por arquivo analisado, com colunas binárias (0 ou 1) indicando a
presença de cada um dos dois smells.

Uso:
    python run_pyexamine.py --input-dir ./saida --output-dir ./resultados/pyexamine
"""

import argparse
import csv
import logging
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

SMELL_NAME_TO_CATEGORY = {
    "Long Method": "long_method",
    "LONG_METHOD": "long_method",
    "Long Parameter List": "long_parameter_list",
    "LONG_PARAMETER_LIST": "long_parameter_list",
}

TARGET_CATEGORIES = ["long_method", "long_parameter_list"]

ALL_CATEGORIES = [
    "data_class", "large_class", "lazy_class",
    "long_method", "long_parameter_list", "magic_numbers",
]


def run_pyexamine(input_dir: Path, output_dir: Path) -> Path:
    """
    Executa o PyExamine local localizado na pasta 'python_smells_detector'
    passando a pasta de saída como base e localiza o arquivo CSV gerado.
    """
    # Diretório raiz do script atual (EXTRATOR_ARQPY)
    base_dir = Path(__file__).parent.resolve()
    
    # Caminho do repositório local do PyExamine
    pyexamine_repo_dir = base_dir / "python_smells_detector"
    
    # Caminho dinâmico para o arquivo de configuração YAML
    config_file = base_dir / "code_quality_config.yaml"

    raw_prefix = output_dir / "pyexamine_raw"
    
    cmd = [
        sys.executable, "-m", "code_quality_analyzer.main",
        str(input_dir),
        "--output", str(raw_prefix),
        "--type", "code",
        "--config", str(config_file),
        "--ignore", "venv", ".venv", ".git", "__pycache__",
    ]
    
    # Adiciona a pasta local python_smells_detector ao PYTHONPATH da execução
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{pyexamine_repo_dir}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(pyexamine_repo_dir)

    logger.info("Executando PyExamine Local (%s): %s", pyexamine_repo_dir, " ".join(cmd))
    
    result = subprocess.run(cmd, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"O PyExamine finalizou com erro (código {result.returncode}).")

    # Procura qualquer CSV gerado dentro do output_dir ou no diretório pai
    search_dirs = [output_dir, output_dir.parent]
    found_csvs = []

    for d in search_dirs:
        if d.exists():
            found_csvs.extend(list(d.glob("*code_smells*.csv")))
            found_csvs.extend(list(d.glob("pyexamine_raw*.csv")))

    if not found_csvs:
        raise FileNotFoundError(f"Nenhum CSV do PyExamine foi localizado em {output_dir} nem em {output_dir.parent}.")

    # Pega o arquivo CSV mais recente gerado
    raw_csv = max(found_csvs, key=lambda p: p.stat().st_mtime)
    logger.info("CSV bruto encontrado: %s", raw_csv)
    return raw_csv


def normalize(raw_csv: Path, input_dir: Path) -> list[dict]:
    per_file_smells = defaultdict(set)

    with raw_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row.get("File", "").strip()
            smell_name = row.get("Name", "").strip()
            if not file_path:
                continue
            filename = Path(file_path).name
            
            category = SMELL_NAME_TO_CATEGORY.get(smell_name)
            if category:
                per_file_smells[filename].add(category)

    all_files = sorted(p.name for p in input_dir.glob("*.py"))

    rows = []
    for filename in all_files:
        found = per_file_smells.get(filename, set())
        row = {"generated_filename": filename}
        
        for cat in ALL_CATEGORIES:
            if cat in TARGET_CATEGORIES:
                row[f"pyexamine_{cat}"] = int(cat in found)
            else:
                row[f"pyexamine_{cat}"] = "" 

        rows.append(row)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roda o PyExamine local e normaliza a saída.")
    parser.add_argument("--input-dir", required=True, help="Pasta com os .py gerados.")
    parser.add_argument("--output-dir", default="./resultados/pyexamine", help="Pasta de saída.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_csv = run_pyexamine(input_dir, output_dir)

    rows = normalize(raw_csv, input_dir)

    per_file_csv = output_dir / "pyexamine_per_file.csv"
    fieldnames = ["generated_filename"] + [f"pyexamine_{c}" for c in ALL_CATEGORIES]
    with per_file_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Concluído! Arquivo final gerado em: %s (%d arquivos processados)", per_file_csv, len(rows))


if __name__ == "__main__":
    main()