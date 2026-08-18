#!/usr/bin/env python3
"""
build_experts_csv.py

Lê os 6 CSVs originais do dataset pyhub-smell contendo as avaliações dos especialistas e
consolida os resultados em um único arquivo 'experts_ground_truth.csv' (Ground Truth /
Gabarito), utilizado como referência na comparação com as detecções produzidas por cada
ferramenta avaliada (run_dpy.py, run_pyexamine.py, run_scylla.py e run_sonarqube.py).

Colunas de saída:
- generated_filename: Nome sanitizado do arquivo gerado ({file_name}_{created_at}.py)
- expert_data_class
- expert_large_class
- expert_lazy_class
- expert_long_method
- expert_long_parameter_list
- expert_magic_numbers

Uso:
    python build_experts_csv.py --input-dir ./CSVs --output-file ./resultados/experts_ground_truth.csv
"""

import argparse
import csv
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

DEFAULT_CSV_FILES = [
    "mistral_data_class_zero_shot_without_ast.csv",
    "mistral_large_class_zero_shot_without_ast.csv",
    "mistral_lazy_class_zero_shot_without_ast.csv",
    "mistral_long_method_zero_shot_without_ast.csv",
    "mistral_long_parameter_list_zero_shot_without_ast.csv",
    "mistral_magic_numbers_zero_shot_without_ast.csv",
]

SMELL_CATEGORIES = [
    "data_class",
    "large_class",
    "lazy_class",
    "long_method",
    "long_parameter_list",
    "magic_numbers",
]


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\-.]", "_", name)
    name = re.sub(r"_{2,}", "_", name)
    return name


def detect_smell_category(csv_name: str) -> str:
    name_lower = csv_name.lower()
    for cat in SMELL_CATEGORIES:
        if cat in name_lower:
            return cat
    return ""


def parse_expert_value(val: str) -> int:
    if not val:
        return 0
    val_clean = str(val).strip().lower()
    if val_clean in ("1", "true", "yes", "y", "sim", "s"):
        return 1
    return 0


def process_csvs(input_dir: Path, csv_names: list[str]) -> list[dict]:
    # Estrutura: file_id -> { category: int }
    ground_truth = defaultdict(lambda: {cat: 0 for cat in SMELL_CATEGORIES})

    for name in csv_names:
        csv_path = Path(name)
        if not csv_path.is_absolute() and not csv_path.exists():
            csv_path = input_dir / name

        if not csv_path.exists():
            logger.warning("CSV não encontrado, pulando: %s", csv_path)
            continue

        active_category = detect_smell_category(csv_path.name)
        if not active_category:
            logger.warning("Não foi possível identificar a categoria do smell para %s", csv_path.name)
            continue

        logger.info("Processando %s (categoria: %s)", csv_path.name, active_category)

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_name = (row.get("file_name") or "").strip()
                created_at = (row.get("created_at") or "").strip()
                expert_raw = row.get("expert")

                if not file_name or not created_at:
                    continue

                # Recria a chave/nome do arquivo .py correspondente
                base_name = sanitize_filename(f"{file_name}_{created_at}")
                if not base_name.lower().endswith(".py"):
                    base_name += ".py"

                expert_val = parse_expert_value(expert_raw)
                ground_truth[base_name][active_category] = expert_val

    # Converte em lista de dicionários para exportar
    rows = []
    for filename in sorted(ground_truth.keys()):
        row = {"generated_filename": filename}
        for cat in SMELL_CATEGORIES:
            row[f"expert_{cat}"] = ground_truth[filename][cat]
        rows.append(row)

    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera o arquivo CSV de Ground Truth com avaliações dos experts.")
    parser.add_argument("csv_files", nargs="*", help="Arquivos CSV a processar.")
    parser.add_argument("--input-dir", default=".", help="Diretório onde os CSVs estão localizados.")
    parser.add_argument("--output-file", default="./experts_ground_truth.csv", help="Caminho do arquivo final de saída.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    csv_names = args.csv_files if args.csv_files else DEFAULT_CSV_FILES
    rows = process_csvs(input_dir, csv_names)

    fieldnames = ["generated_filename"] + [f"expert_{cat}" for cat in SMELL_CATEGORIES]

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Ground Truth exportado com sucesso: %s (%d arquivos registrados)", output_file, len(rows))


if __name__ == "__main__":
    main()  