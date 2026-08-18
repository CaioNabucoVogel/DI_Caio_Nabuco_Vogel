#!/usr/bin/env python3
"""
csv_to_py.py

Lê um ou mais arquivos CSV (com colunas: id, smell_type, explanation, file_name,
model, programming_language, class_name, method_name, analyse_type, code,
prompt_type, prompt, is_composite_prompt, code_metric, created_at, expert)
e gera, para cada linha, um arquivo .py contendo o conteúdo da coluna "code".

Nome do arquivo gerado: "{file_name}_{created_at}__{sufixo_expert}.py"
onde {sufixo_expert} é uma sequência de 6 valores (0 ou 1) representando
a avaliação da coluna 'expert' para cada uma das 6 categorias:
[data_class, large_class, lazy_class, long_method, long_parameter_list, magic_numbers]

Uso:
    python csv_to_py.py
    python csv_to_py.py --input-dir ./CSVs --output-dir ./saida
    python csv_to_py.py arquivo1.csv arquivo2.csv --output-dir ./saida

Se nenhum CSV for passado como argumento, o script tentará processar a lista
padrão definida em DEFAULT_CSV_FILES, procurando-os em --input-dir.
"""

import argparse
import csv
import logging
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

DEFAULT_CSV_FILES = [
    "mistral_data_class_zero_shot_without_ast.csv",
    "mistral_large_class_zero_shot_without_ast.csv",
    "mistral_lazy_class_zero_shot_without_ast.csv",
    "mistral_long_method_zero_shot_without_ast.csv",
    "mistral_long_parameter_list_zero_shot_without_ast.csv",
    "mistral_magic_numbers_zero_shot_without_ast.csv",
]

# Ordem fixa dos 6 code smells para formar a combinação no nome do arquivo
SMELL_CATEGORIES_ORDER = [
    "data_class",
    "large_class",
    "lazy_class",
    "long_method",
    "long_parameter_list",
    "magic_numbers",
]

REQUIRED_COLUMNS = {"file_name", "created_at", "code", "expert"}

# csv.field_size_limit padrão é pequeno demais para colunas "code" grandes
csv.field_size_limit(sys.maxsize)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def sanitize_filename(name: str) -> str:
    """
    Remove/normaliza caracteres inválidos ou problemáticos para nomes de
    arquivo (ex: ':' em timestamps, espaços, barras, etc.).
    """
    name = name.strip()
    # Substitui qualquer caractere que não seja letra, número, '_', '-' ou '.'
    name = re.sub(r"[^\w\-.]", "_", name)
    # Evita underscores repetidos em excesso
    name = re.sub(r"_{2,}", "_", name)
    return name


def detect_smell_category(csv_name: str) -> str:
    """
    Identifica qual a categoria de smell com base no nome do arquivo CSV.
    """
    name_lower = csv_name.lower()
    for cat in SMELL_CATEGORIES_ORDER:
        if cat in name_lower:
            return cat
    return ""


def parse_expert_value(val: str) -> int:
    """
    Normaliza a coluna expert para 1 (positivo/detectado) ou 0 (ausente/falso).
    """
    if not val:
        return 0
    val_clean = str(val).strip().lower()
    if val_clean in ("1", "true", "yes", "y", "sim", "s"):
        return 1
    return 0


def build_expert_suffix(active_category: str, expert_val: int) -> str:
    """
    Gera o sufixo de 6 posições no formato '__0_1_0_0_0_0' de acordo com a
    posição do smell ativo no arquivo CSV.
    """
    vector = [0] * len(SMELL_CATEGORIES_ORDER)
    if active_category in SMELL_CATEGORIES_ORDER:
        idx = SMELL_CATEGORIES_ORDER.index(active_category)
        vector[idx] = expert_val

    return "__" + "_".join(str(v) for v in vector)


def build_output_filename(file_name: str, created_at: str, active_category: str, expert_raw: str) -> str:
    base = f"{file_name}_{created_at}"
    base = sanitize_filename(base)

    expert_val = parse_expert_value(expert_raw)
    suffix = build_expert_suffix(active_category, expert_val)

    final_name = f"{base}{suffix}"
    if not final_name.lower().endswith(".py"):
        final_name += ".py"

    return final_name


def resolve_unique_path(directory: Path, filename: str) -> Path:
    """
    Se já existir um arquivo com esse nome no diretório, adiciona um sufixo
    numérico incremental para evitar sobrescrever dados de outras linhas/CSVs.
    """
    candidate = directory / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        new_candidate = directory / f"{stem}__{counter}{suffix}"
        if not new_candidate.exists():
            return new_candidate
        counter += 1


def process_csv(csv_path: Path, output_dir: Path) -> tuple[int, int]:
    """
    Processa um único CSV, gerando um arquivo .py por linha com a
    avaliação do expert codificada no nome.
    Retorna (linhas_processadas, linhas_com_erro).
    """
    if not csv_path.exists():
        logger.warning("Arquivo não encontrado, pulando: %s", csv_path)
        return 0, 0

    logger.info("Processando: %s", csv_path.name)
    active_category = detect_smell_category(csv_path.name)

    if active_category:
        logger.info("Categoria de smell identificada para %s: '%s'", csv_path.name, active_category)
    else:
        logger.warning("Não foi possível identificar a categoria do smell em %s. Sufixo expert será zerado.", csv_path.name)

    ok_count = 0
    error_count = 0

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            logger.error(
                "Colunas obrigatórias ausentes em %s: %s. Pulando arquivo.",
                csv_path.name,
                ", ".join(sorted(missing)),
            )
            return 0, 0

        for i, row in enumerate(reader, start=2):  # linha 1 = cabeçalho
            file_name = (row.get("file_name") or "").strip()
            created_at = (row.get("created_at") or "").strip()
            code = row.get("code")
            expert_raw = row.get("expert")

            if not file_name or not created_at:
                logger.warning(
                    "[%s linha %d] 'file_name' ou 'created_at' vazio. Pulando.",
                    csv_path.name, i,
                )
                error_count += 1
                continue

            if code is None:
                logger.warning(
                    "[%s linha %d] coluna 'code' vazia. Pulando.",
                    csv_path.name, i,
                )
                error_count += 1
                continue

            out_filename = build_output_filename(file_name, created_at, active_category, expert_raw)
            out_path = resolve_unique_path(output_dir, out_filename)

            try:
                out_path.write_text(code, encoding="utf-8")
                ok_count += 1
            except OSError as exc:
                logger.error(
                    "[%s linha %d] falha ao escrever '%s': %s",
                    csv_path.name, i, out_path, exc,
                )
                error_count += 1

    logger.info(
        "Concluído %s: %d arquivo(s) gerado(s), %d erro(s).",
        csv_path.name, ok_count, error_count,
    )
    return ok_count, error_count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converte a coluna 'code' de arquivos CSV em arquivos .py individuais com sufixo da avaliação do expert."
    )
    parser.add_argument(
        "csv_files",
        nargs="*",
        help="Nomes/caminhos dos CSVs a processar. Se omitido, usa a lista padrão.",
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Diretório onde os CSVs estão localizados (padrão: diretório atual).",
    )
    parser.add_argument(
        "--output-dir",
        default="./output_py",
        help="Diretório onde os arquivos .py serão criados (padrão: ./output_py).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_names = args.csv_files if args.csv_files else DEFAULT_CSV_FILES

    total_ok = 0
    total_err = 0
    for name in csv_names:
        csv_path = Path(name)
        if not csv_path.is_absolute() and not csv_path.exists():
            csv_path = input_dir / name
        ok, err = process_csv(csv_path, output_dir)
        total_ok += ok
        total_err += err

    logger.info(
        "Resumo final: %d arquivo(s) .py gerado(s) em '%s', %d erro(s) no total.",
        total_ok, output_dir, total_err,
    )


if __name__ == "__main__":
    main()