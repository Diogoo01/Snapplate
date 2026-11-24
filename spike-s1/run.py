"""Spike S1/S2 (#4, #8): compare vision models on fridge photos.

Disposable spike code. Uses only the Python standard library.

Usage (from the repo root):
    python spike-s1/run.py --list-models
    python spike-s1/run.py --gemini gemini-model-id --openrouter some/model:free

Reads API keys from the .env file at the repo root (never printed):
    GEMINI_API_KEY=...
    OPENROUTER_API_KEY=...
Photos are read from evals/photos/ (ignored by git).
Expected ingredients are read from spike-s1/expected.json.
"""

import argparse
import base64
import json
import mimetypes
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHOTOS_DIR = ROOT / "evals" / "photos"
EXPECTED_FILE = Path(__file__).resolve().parent / "expected.json"
RESULTS_DIR = Path(__file__).resolve().parent / "results"

PROMPT = (
    "És um assistente de cozinha. Identifica todos os ingredientes alimentares "
    "visíveis nesta foto de um frigorífico ou despensa. Ignora embalagens que "
    "não consigas identificar. Responde APENAS com JSON válido no formato: "
    '{"ingredients": [{"name": "nome em português de Portugal, singular, '
    'minúsculas", "confidence": 0.0}]}'
)

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def load_env() -> dict:
    env = {}
    env_file = ROOT / ".env"
    if not env_file.exists():
        return env
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def http_json(url: str, headers: dict, body: dict | None = None, timeout: int = 120) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    if data:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {error.code}: {detail}") from None


def normalize(name: str) -> str:
    text = unicodedata.normalize("NFKD", name.lower().strip())
    return "".join(c for c in text if not unicodedata.combining(c))


def parse_ingredients(text: str) -> list[str]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in response")
    payload = json.loads(text[start : end + 1])
    return [item["name"] for item in payload.get("ingredients", []) if item.get("name")]


def call_gemini(model: str, key: str, image_b64: str, mime: str) -> str:
    body = {
        "contents": [{"parts": [{"text": PROMPT}, {"inline_data": {"mime_type": mime, "data": image_b64}}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    result = http_json(f"{GEMINI_BASE}/models/{model}:generateContent", {"x-goog-api-key": key}, body)
    return result["candidates"][0]["content"]["parts"][0]["text"]


def call_openrouter(model: str, key: str, image_b64: str, mime: str) -> str:
    body = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
                ],
            }
        ],
    }
    headers = {"Authorization": f"Bearer {key}", "X-Title": "Snapplate spike"}
    result = http_json(f"{OPENROUTER_BASE}/chat/completions", headers, body)
    return result["choices"][0]["message"]["content"]


def list_models(env: dict) -> None:
    if key := env.get("GEMINI_API_KEY"):
        models = http_json(f"{GEMINI_BASE}/models?pageSize=1000", {"x-goog-api-key": key}).get("models", [])
        print("Gemini (generateContent):")
        for m in models:
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(f"  {m['name'].removeprefix('models/')}")
    else:
        print("GEMINI_API_KEY em falta no .env")
    models = http_json(f"{OPENROUTER_BASE}/models", {}).get("data", [])
    print("OpenRouter (gratuitos com imagem):")
    for m in models:
        modalities = m.get("architecture", {}).get("input_modalities", [])
        if m["id"].endswith(":free") and "image" in modalities:
            print(f"  {m['id']}")


def score(found: list[str], expected: dict) -> dict:
    """expected: {"ingredients": {"tomate": ["tomates", "tomato"], ...}}"""
    found_norm = {normalize(f) for f in found}
    matched, missed = [], []
    used = set()
    for name, synonyms in expected["ingredients"].items():
        variants = {normalize(name), *(normalize(s) for s in synonyms)}
        hit = next((f for f in found_norm if f in variants or any(v in f for v in variants)), None)
        if hit:
            matched.append(name)
            used.add(hit)
        else:
            missed.append(name)
    extra = sorted(found_norm - used)
    total = len(expected["ingredients"]) or 1
    return {
        "recall": round(len(matched) / total, 3),
        "matched": matched,
        "missed": missed,
        "extra": extra,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--gemini", action="append", default=[], help="Gemini model id (repeatable)")
    parser.add_argument("--openrouter", action="append", default=[], help="OpenRouter model id (repeatable)")
    parser.add_argument("--limit", type=int, default=0, help="only the first N photos")
    args = parser.parse_args()

    env = load_env()
    if args.list_models:
        list_models(env)
        return 0

    expected_all = json.loads(EXPECTED_FILE.read_text(encoding="utf-8"))
    photos = sorted(p for p in PHOTOS_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    if args.limit:
        photos = photos[: args.limit]

    runners = [("gemini", m, call_gemini, env.get("GEMINI_API_KEY")) for m in args.gemini]
    runners += [("openrouter", m, call_openrouter, env.get("OPENROUTER_API_KEY")) for m in args.openrouter]
    if not runners:
        print("Indica pelo menos um modelo (--gemini / --openrouter).")
        return 1

    rows = []
    for photo in photos:
        expected = expected_all.get(photo.name)
        if not expected:
            print(f"[aviso] {photo.name} sem anotação em expected.json — ignorada")
            continue
        mime = mimetypes.guess_type(photo.name)[0] or "image/jpeg"
        image_b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
        for provider, model, call, key in runners:
            if not key:
                print(f"[erro] chave em falta para {provider}")
                continue
            started = time.perf_counter()
            row = {"photo": photo.name, "provider": provider, "model": model}
            try:
                text = call(model, key, image_b64, mime)
                row["latency_s"] = round(time.perf_counter() - started, 2)
                found = parse_ingredients(text)
                row["valid_json"] = True
                row["found"] = found
                row.update(score(found, expected))
            except Exception as error:  # spike: record and continue
                row["latency_s"] = round(time.perf_counter() - started, 2)
                row["valid_json"] = False
                row["error"] = str(error)[:300]
            rows.append(row)
            status = f"recall={row.get('recall')}" if row["valid_json"] else f"ERRO {row['error'][:80]}"
            print(f"{photo.name:<24} {provider}:{model:<45} {row['latency_s']:>6}s  {status}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"results-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nResumo por modelo:")
    for provider, model, _, _ in runners:
        mine = [r for r in rows if r["model"] == model]
        ok = [r for r in mine if r["valid_json"]]
        if not mine:
            continue
        recall = sum(r["recall"] for r in ok) / len(ok) if ok else 0
        latency = sum(r["latency_s"] for r in ok) / len(ok) if ok else 0
        extras = sum(len(r["extra"]) for r in ok)
        print(
            f"  {provider}:{model}: recall médio {recall:.0%}, latência média {latency:.1f}s, "
            f"JSON válido {len(ok)}/{len(mine)}, extras {extras}"
        )
    print(f"\nResultados em {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
