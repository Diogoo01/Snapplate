"""Spike S3 (#5): does structured output always return valid JSON?

Disposable spike code. Compares two modes on the same photos and prompt:
  prompt  - format described only in the prompt (+ responseMimeType JSON), as in S1
  schema  - same prompt + the JSON Schema sent to the API (responseJsonSchema)
Each response is validated against spike-s3/schema.json with the jsonschema package.

Usage (from the repo root, with the spike venv):
    spike-s3/.venv/Scripts/python spike-s3/run.py --mode prompt --calls 50
    spike-s3/.venv/Scripts/python spike-s3/run.py --mode schema --calls 50
"""

import argparse
import base64
import json
import mimetypes
import sys
import time
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "spike-s1"))
import run as s1  # noqa: E402  (reuses .env loading, HTTP retries and scoring)

SCHEMA = json.loads((HERE / "schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)
RESULTS_DIR = HERE / "results"
MODEL = "gemini-3.5-flash-lite"
MIN_INTERVAL_S = 4.5  # free tier: 15 requests/min

PROMPT = (
    "És um assistente de cozinha. Analisa esta foto de um frigorífico, despensa "
    "ou bancada e lista todos os alimentos e bebidas que lá estão.\n"
    "Método:\n"
    "1. Percorre a imagem por zonas: prateleira a prateleira, de cima para baixo, "
    "incluindo a porta, o fundo e os cantos.\n"
    "2. Em cada zona, lê os rótulos e textos das embalagens (pacotes, frascos, "
    "latas, garrafas, caixas, sacos) para identificar o produto, mesmo que a "
    "embalagem esteja fechada.\n"
    "3. Inclui itens pequenos ou parcialmente tapados se os conseguires reconhecer.\n"
    "Regras:\n"
    "- Inclui apenas alimentos e bebidas; ignora objetos que não se comem "
    "(medicamentos, produtos de limpeza, decoração), mesmo que pareçam alimentos.\n"
    "- Não adivinhes o conteúdo de recipientes opacos sem rótulo.\n"
    "- Usa o nome genérico do produto, nunca a marca.\n"
    "- Estima a quantidade visível: amount é um número maior que 0 e unit é uma "
    "de: unidade, g, kg, ml, l, embalagem.\n"
    "- confidence vai de 0 a 1; usa valores baixos quando não tens a certeza.\n"
    "- photoQuality.rating é 'poor' se a foto não permitir identificar bem os "
    "ingredientes (pouca luz, desfocada, demasiado longe); reason explica em poucas palavras.\n"
    "Responde APENAS com JSON válido no formato:\n"
    '{"photoQuality": {"rating": "good", "reason": "..."}, '
    '"ingredients": [{"name": "...", "quantity": {"amount": 1, "unit": "unidade"}, '
    '"confidence": 0.9}]}'
)


def call(mode: str, key: str, image_b64: str, mime: str) -> str:
    config = {"responseMimeType": "application/json", "temperature": 0}
    if mode == "schema":
        config["responseJsonSchema"] = SCHEMA
    body = {
        "contents": [{"parts": [{"text": PROMPT}, {"inline_data": {"mime_type": mime, "data": image_b64}}]}],
        "generationConfig": config,
    }
    result = s1.http_json(f"{s1.GEMINI_BASE}/models/{MODEL}:generateContent", {"x-goog-api-key": key}, body)
    return result["candidates"][0]["content"]["parts"][0]["text"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["prompt", "schema"], required=True)
    parser.add_argument("--calls", type=int, default=50)
    args = parser.parse_args()

    key = s1.load_env().get("GEMINI_API_KEY")
    if not key:
        print("GEMINI_API_KEY em falta no .env")
        return 1
    expected_all = json.loads(s1.EXPECTED_FILE.read_text(encoding="utf-8"))
    photos = sorted(p for p in s1.PHOTOS_DIR.iterdir() if p.name in expected_all)
    images = {p.name: base64.b64encode(p.read_bytes()).decode("ascii") for p in photos}

    rows, last_call = [], 0.0
    for i in range(args.calls):
        photo = photos[i % len(photos)]
        wait = MIN_INTERVAL_S - (time.monotonic() - last_call)
        if wait > 0:
            time.sleep(wait)
        last_call = time.monotonic()
        row = {"call": i + 1, "photo": photo.name, "mode": args.mode}
        started = time.perf_counter()
        try:
            text = call(args.mode, key, images[photo.name], mimetypes.guess_type(photo.name)[0] or "image/jpeg")
            row["latency_s"] = round(time.perf_counter() - started, 2)
            row["raw"] = text
            try:
                payload = json.loads(text)  # strict: the whole response must be JSON
            except json.JSONDecodeError as error:
                row["status"] = "invalid_json"
                row["errors"] = [str(error)]
            else:
                errors = sorted(VALIDATOR.iter_errors(payload), key=lambda e: list(e.path))
                if errors:
                    row["status"] = "schema_error"
                    row["errors"] = [f"{'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}"[:200] for e in errors[:10]]
                else:
                    row["status"] = "valid"
                    row["photo_quality"] = payload["photoQuality"]["rating"]
                    row["n_ingredients"] = len(payload["ingredients"])
                    names = [item["name"] for item in payload["ingredients"]]
                    row["recall"] = s1.score(names, expected_all[photo.name])["recall"]
        except s1.UnavailableError as error:
            row["status"] = "unavailable"
            row["errors"] = [str(error)[:200]]
        except Exception as error:  # spike: record and continue
            row["status"] = "error"
            row["errors"] = [str(error)[:200]]
        row.setdefault("latency_s", round(time.perf_counter() - started, 2))
        rows.append(row)
        detail = row.get("errors", [""])[0][:80] if row["status"] != "valid" else f"recall={row['recall']}"
        print(f"{i + 1:>3} {photo.name:<12} {row['latency_s']:>6}s  {row['status']:<13} {detail}", flush=True)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"results-{args.mode}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    answered = [r for r in rows if r["status"] in {"valid", "invalid_json", "schema_error"}]
    valid = [r for r in rows if r["status"] == "valid"]
    print(f"\nModo {args.mode}: {counts}")
    if answered:
        print(f"  válidas {len(valid)}/{len(answered)} respostas recebidas")
    if valid:
        print(f"  recall médio {sum(r['recall'] for r in valid) / len(valid):.0%}, "
              f"latência média {sum(r['latency_s'] for r in valid) / len(valid):.1f}s, "
              f"fotos 'poor': {sum(r['photo_quality'] == 'poor' for r in valid)}")
    print(f"Resultados em {out.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
