#!/usr/bin/env python3
"""
run_sonarqube.py

Executa o SonarScanner local contra uma instância do SonarQube rodando em container
Docker, analisando os arquivos .py gerados por csv_to_py.py. Como o SonarQube identifica
o smell 'Long Parameter List' sob o nome 'Excessive Parameter List', o script realiza
esse mapeamento de nomenclatura ao extrair os resultados.

As detecções de 'Long Method' e 'Long Parameter List' retornadas pela API do SonarQube
são normalizadas em um CSV "largo", com uma linha por arquivo analisado.

Uso:
    python run_sonarqube.py --input-dir ./saida --output-dir ./resultados/sonarqube
"""

import argparse
import csv
import json
import logging
import subprocess
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# Mapeamento de regras do SonarQube para as nossas categorias
SONAR_RULE_MAPPING = {
    "python:S107": "sonar_long_parameter_list",
    "python:S138": "sonar_long_method",
    "python:S3776": "sonar_long_method",       
    "python:S1172": "sonar_long_parameter_list",
    "python:S1186": "sonar_lazy_class",        
    "python:S1700": "sonar_data_class",
}

TARGET_CATEGORIES = ["long_method", "long_parameter_list"]

ALL_CATEGORIES = [
    "data_class", "large_class", "lazy_class",
    "long_method", "long_parameter_list", "magic_numbers",
]


def find_sonar_scanner(base_dir: Path) -> str:
    """
    Localiza o executável do SonarScanner no diretório do projeto ou no PATH.
    """
    # Procura especificamente pela pasta do scanner visível na imagem
    scanner_folders = list(base_dir.glob("sonar-scanner*"))
    if scanner_folders:
        bat_path = scanner_folders[0] / "bin" / "sonar-scanner.bat"
        if bat_path.exists():
            return str(bat_path)

    # Fallback para o comando global do sistema
    return "sonar-scanner"


def run_sonar_scanner(input_dir: Path, project_key: str, host_url: str, token: str) -> None:
    """
    Executa a análise estática usando o SonarScanner local.
    """
    base_dir = Path(__file__).parent.resolve()
    scanner_bin = find_sonar_scanner(base_dir)

    cmd = [
        scanner_bin,
        f"-Dsonar.projectKey={project_key}",
        f"-Dsonar.sources={input_dir.resolve()}",
        f"-Dsonar.host.url={host_url}",
        "-Dsonar.sourceEncoding=UTF-8",
    ]
    
    if token:
        # Para o SonarQube 9.9 com SonarScanner CLI 8, o parâmetro correto de autenticação é sonar.login
        cmd.append(f"-Dsonar.login={token}")

    logger.info("Executando SonarScanner através de: %s", scanner_bin)
    
    # Executa passando a lista de argumentos diretamente (evita problemas com acentos em caminhos no shell)
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        encoding="utf-8", 
        errors="replace"
    )

    if result.returncode != 0:
        logger.error("Erro ao executar o SonarScanner:")
        logger.error("STDOUT: %s", result.stdout)
        logger.error("STDERR: %s", result.stderr)
        raise RuntimeError(f"O SonarScanner falhou com código de saída {result.returncode}")

    logger.info("Análise do SonarScanner concluída com sucesso.")

def fetch_sonar_issues(project_key: str, host_url: str, token: str) -> dict[str, set]:
    """
    Consulta a API REST do SonarQube para extrair as regras violadas.
    """
    per_file_smells = defaultdict(set)
    page = 1
    page_size = 500

    base_url = host_url.rstrip("/") + "/api/issues/search"

    while True:
        params = {
            "componentKeys": project_key,
            "types": "CODE_SMELL",
            "ps": str(page_size),
            "p": str(page),
        }

        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url)

        if token:
            import base64
            auth = base64.b64encode(f"{token}:".encode("utf-8")).decode("utf-8")
            req.add_header("Authorization", f"Basic {auth}")

        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.error("Falha ao se comunicar com a API do SonarQube em %s: %s", url, e)
            raise

        issues = data.get("issues", [])
        if not issues:
            break

        for issue in issues:
            rule = issue.get("rule", "")
            component = issue.get("component", "")  # Ex: projectKey:saida/filename.py
            
            category = SONAR_RULE_MAPPING.get(rule)
            if category:
                filename = Path(component.split(":")[-1]).name
                per_file_smells[filename].add(category)

        total = data.get("paging", {}).get("total", 0)
        if page * page_size >= total:
            break

        page += 1

    return per_file_smells


def normalize(per_file_smells: dict[str, set], input_dir: Path) -> list[dict]:
    all_files = sorted(p.name for p in input_dir.glob("*.py"))
    rows = []

    for filename in all_files:
        found = per_file_smells.get(filename, set())
        row = {"generated_filename": filename}

        for cat in ALL_CATEGORIES:
            if cat in TARGET_CATEGORIES:
                row[f"sonar_{cat}"] = int(cat in found)
            else:
                row[f"sonar_{cat}"] = ""  # Mantém em branco para categorias fora de escopo

        rows.append(row)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roda o SonarScanner e extrai o CSV normalizado do SonarQube.")
    parser.add_argument("--input-dir", default="./saida", help="Pasta com os arquivos .py a serem analisados.")
    parser.add_argument("--output-dir", default="./resultados/sonarqube", help="Pasta para salvar os relatórios.")
    parser.add_argument("--host-url", default="http://localhost:9000", help="URL do servidor do SonarQube.")
    parser.add_argument("--project-key", default="extrator_arqpy", help="Chave do projeto no SonarQube.")
    parser.add_argument("--token", default="", help="Token de autenticação (se o SonarQube exigir).")
    parser.add_argument("--skip-scan", action="store_true", help="Apenas lê a API sem rodar o scanner novamente.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_scan:
        run_sonar_scanner(input_dir, args.project_key, args.host_url, args.token)
        logger.info("Aguardando indexação dos resultados pelo servidor SonarQube...")
        time.sleep(3)

    logger.info("Coletando os resultados via API do SonarQube...")
    per_file_smells = fetch_sonar_issues(args.project_key, args.host_url, args.token)

    rows = normalize(per_file_smells, input_dir)

    per_file_csv = output_dir / "sonar_per_file.csv"
    fieldnames = ["generated_filename"] + [f"sonar_{c}" for c in ALL_CATEGORIES]

    with per_file_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Processamento concluído! Relatório final salvo em: %s (%d arquivos)", per_file_csv, len(rows))


if __name__ == "__main__":
    main()