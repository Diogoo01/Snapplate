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

JSON_FORMAT = (
    'Responde APENAS com JSON válido no formato: '
    '{"ingredients": [{"name": "nome em português de Portugal, singular, '
    'minúsculas", "confidence": 0.0}]}'
)

PROMPTS = {
    # v1: first baseline.
    "v1": (
        "És um assistente de cozinha. Identifica todos os ingredientes alimentares "
        "visíveis nesta foto de um frigorífico ou despensa. Ignora embalagens que "
        "não consigas identificar. " + JSON_FORMAT
    ),
    # v2: systematic scan by zone + read labels of closed packages.
    "v2": (
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
        "- confidence vai de 0 a 1; usa valores baixos quando não tens a certeza.\n"
        + JSON_FORMAT
    ),
}
PROMPT = PROMPTS["v1"]

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


RETRY_STATUSES = {429, 500, 502, 503, 504}
RETRY_WAITS_S = [5, 15, 30]


class UnavailableError(RuntimeError):
    """The provider was unavailable (rate limit / overload) after all retries."""


def http_json(url: str, headers: dict, body: dict | None = None, timeout: int = 120) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(len(RETRY_WAITS_S) + 1):
        request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
        if data:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:500]
            if error.code in RETRY_STATUSES:
                if attempt < len(RETRY_WAITS_S):
                    time.sleep(RETRY_WAITS_S[attempt])
                    continue
                raise UnavailableError(f"HTTP {error.code} after {attempt + 1} attempts: {detail}") from None
            raise RuntimeError(f"HTTP {error.code}: {detail}") from None
    raise AssertionError("unreachable")


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
    all_variants = set()
    for name, synonyms in expected["ingredients"].items():
        variants = {normalize(name), *(normalize(s) for s in synonyms)}
        all_variants |= variants
        if any(f in variants or any(v in f for v in variants) for f in found_norm):
            matched.append(name)
        else:
            missed.append(name)
    # Extra = found items that match no expected ingredient at all (possible hallucinations).
    extra = sorted(f for f in found_norm if not (f in all_variants or any(v in f for v in all_variants)))
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
    parser.add_argument("--prompt", choices=sorted(PROMPTS), default="v1", help="prompt version")
    args = parser.parse_args()

    global PROMPT
    PROMPT = PROMPTS[args.prompt]

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
            row = {"photo": photo.name, "provider": provider, "model": model, "prompt": args.prompt}
            text = None
            try:
                text = call(model, key, image_b64, mime)
                row["latency_s"] = round(time.perf_counter() - started, 2)
                found = parse_ingredients(text)
                row["status"] = "ok"
                row["found"] = found
                row.update(score(found, expected))
            except UnavailableError as error:
                row["status"] = "unavailable"
                row["error"] = str(error)[:300]
            except Exception as error:  # spike: record and continue
                row["status"] = "invalid" if text is not None else "error"
                row["error"] = str(error)[:300]
            row.setdefault("latency_s", round(time.perf_counter() - started, 2))
            rows.append(row)
            status = f"recall={row.get('recall')}" if row["status"] == "ok" else f"{row['status'].upper()} {row['error'][:70]}"
            print(f"{photo.name:<24} {provider}:{model:<45} {row['latency_s']:>6}s  {status}")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"results-{args.prompt}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nResumo por modelo (prompt {args.prompt}):")
    for provider, model, _, _ in runners:
        mine = [r for r in rows if r["model"] == model]
        if not mine:
            continue
        ok = [r for r in mine if r["status"] == "ok"]
        unavailable = sum(r["status"] == "unavailable" for r in mine)
        invalid = sum(r["status"] == "invalid" for r in mine)
        recall = sum(r["recall"] for r in ok) / len(ok) if ok else 0
        latency = sum(r["latency_s"] for r in ok) / len(ok) if ok else 0
        extras = sum(len(r["extra"]) for r in ok)
        print(
            f"  {provider}:{model}: ok {len(ok)}/{len(mine)} (indisponível {unavailable}, JSON inválido {invalid}), "
            f"recall médio {recall:.0%}, latência média {latency:.1f}s, extras {extras}"
        )
    print(f"\nResultados em {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
