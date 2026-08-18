#!/usr/bin/env python3
"""
run_dpy.py

Executa o binário compilado do DPy (ferramenta apresentada em Bolouri & Sharma, MSR 2025)
sobre os arquivos .py gerados por csv_to_py.py, extraindo as detecções dos smells
'Long Method' e 'Long Parameter List' relatadas pela ferramenta.

Os resultados brutos retornados pelo DPy são normalizados para um CSV "largo": uma linha
por arquivo analisado, com colunas binárias (0 ou 1) indicando a presença de cada um dos
dois smells, em um formato compatível com o CSV de referência produzido por
build_experts_csv.py.

Uso:
    python run_dpy.py --input-dir ./saida --output-dir ./resultados/dpy
"""

import argparse
import csv
import logging
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# Mapeamento dos nomes de smells do DPy
SMELL_NAME_TO_CATEGORY = {
    # Long Method
    "Long Method": "long_method",
    "LONG_METHOD": "long_method",
    "long_method": "long_method",
    # Long Parameter List
    "Long Parameter List": "long_parameter_list",
    "LONG_PARAMETER_LIST": "long_parameter_list",
    "long_parameter_list": "long_parameter_list",
}

TARGET_CATEGORIES = [
    "long_method", 
    "long_parameter_list"
]

ALL_CATEGORIES = [
    "data_class", 
    "large_class", 
    "lazy_class",
    "long_method", 
    "long_parameter_list", 
    "magic_numbers"
]


def run_dpy(input_dir: Path, output_dir: Path) -> Path:
    """
    Executa o executável DPy fornecido na pasta do projeto.
    """
    base_dir = Path(__file__).parent.resolve()
    
    if sys.platform.startswith("win"):
        dpy_bin = base_dir / "DPy" / "windows" / "dpy.exe"
    else:
        dpy_bin = base_dir / "DPy" / "linux_mac" / "dpy"

    if not dpy_bin.exists():
        dpy_bin = Path("dpy")

    cmd = [
        str(dpy_bin), "analyze",
        "-i", str(input_dir),
        "-o", str(output_dir),
        "-f", "csv"
    ]
    
    logger.info("Executando DPy: %s", " ".join(cmd))
    
    result = subprocess.run(
        cmd, 
        text=True, 
        capture_output=True, 
        encoding="utf-8", 
        errors="replace"
    )

    impl_smells_file = output_dir / f"{input_dir.name}_implementation_smells.csv"
    
    if not impl_smells_file.exists():
        candidates = list(output_dir.glob("*implementation_smells.csv"))
        if candidates:
            impl_smells_file = candidates[0]
        else:
            logger.error("STDOUT: %s", result.stdout)
            logger.error("STDERR: %s", result.stderr)
            raise FileNotFoundError(f"Não foi possível localizar o relatório em {output_dir}")

    logger.info("Relatório de smells de implementação localizado em: %s", impl_smells_file)
    return impl_smells_file


def read_csv_safely(file_path: Path) -> list[dict]:
    """
    Lê o arquivo CSV com suporte a diferentes encodings.
    """
    encodings_to_try = ["utf-8-sig", "cp1252", "latin-1"]
    
    for encoding in encodings_to_try:
        try:
            with file_path.open("r", encoding=encoding, errors="replace") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except UnicodeDecodeError:
            continue
            
    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def normalize(smells_csv: Path, input_dir: Path) -> list[dict]:
    """
    Mapeia os smells encontrados pelo DPy para cada arquivo da pasta de entrada.
    """
    per_file_smells = defaultdict(set)
    rows_data = read_csv_safely(smells_csv)

    logger.info("Total de linhas lidas do CSV bruto do DPy: %d", len(rows_data))

    for row in rows_data:
        file_path = (
            row.get("File") or row.get("File Name") or row.get("Module") or 
            row.get("Module Name") or row.get("file") or row.get("Path") or ""
        )
        smell_name = (
            row.get("Code Smell") or row.get("Smell") or row.get("Smell Name") or 
            row.get("Name") or row.get("smell") or ""
        )
        
        file_path = str(file_path).strip()
        smell_name = str(smell_name).strip()

        if not file_path or not smell_name:
            continue

        filename = Path(file_path).name
        category = SMELL_NAME_TO_CATEGORY.get(smell_name)
        
        if not category:
            for k, v in SMELL_NAME_TO_CATEGORY.items():
                if k.lower() == smell_name.lower():
                    category = v
                    break

        if category:
            per_file_smells[filename].add(category)

    logger.info("Arquivos com smells detectados pelo DPy: %d", len(per_file_smells))

    all_files = sorted(p.name for p in input_dir.glob("*.py"))

    rows = []
    for filename in all_files:
        found = per_file_smells.get(filename, set())
        row = {"generated_filename": filename}
        
        for cat in ALL_CATEGORIES:
            if cat in TARGET_CATEGORIES:
                row[f"dpy_{cat}"] = int(cat in found)
            else:
                row[f"dpy_{cat}"] = ""  # Em branco para fora do escopo

        rows.append(row)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roda o DPy e gera o CSV normalizado.")
    parser.add_argument("--input-dir", default="./saida", help="Pasta contendo os arquivos .py.")
    parser.add_argument("--output-dir", default="./resultados/dpy", help="Pasta para salvar os relatórios.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    impl_smells_csv = run_dpy(input_dir, output_dir)
    rows = normalize(impl_smells_csv, input_dir)

    per_file_csv = output_dir / "dpy_per_file.csv"
    fieldnames = ["generated_filename"] + [f"dpy_{c}" for c in ALL_CATEGORIES]
    
    with per_file_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Processamento concluído! Relatório final em: %s (%d arquivos)", per_file_csv, len(rows))


if __name__ == "__main__":
    main()