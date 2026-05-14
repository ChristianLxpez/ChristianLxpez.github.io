"""
Business Process Analyzer — AI Agent Demo
Christian López Agardi · christianlxpez.github.io

Analiza un proceso de negocio e identifica oportunidades de
automatización con IA usando Google Gemini (gratuito).

SETUP:
  1. pip install google-genai python-dotenv
  2. Crea un archivo .env con:  GEMINI_API_KEY=AIza...
     (o: export GEMINI_API_KEY=AIza...)
  3. python business_process_analyzer.py
"""

import os, json, sys, textwrap

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
except ImportError:
    print("\n  ✗ Instala: pip install google-genai python-dotenv\n")
    sys.exit(1)

# ── ANSI COLORS ───────────────────────────────────────────────────────────────
R   = "\033[0m"
BLD = "\033[1m"
DIM = "\033[2m"
GLD = "\033[38;5;220m"
CYN = "\033[38;5;81m"
GRN = "\033[38;5;82m"
RED = "\033[38;5;196m"
WHT = "\033[97m"
GRY = "\033[90m"

def clr(text, *codes):
    return "".join(codes) + str(text) + R

def box(title, width=64):
    bar = "─" * width
    inner = title.center(width - 2)
    return (
        f"\n{clr('╔' + bar + '╗', GLD)}\n"
        f"{clr('║', GLD)}  {clr(inner, BLD + WHT)}  {clr('║', GLD)}\n"
        f"{clr('╚' + bar + '╝', GLD)}\n"
    )

def divider(width=62):
    return clr("  " + "·" * width, GRY)

def section_header(icon, title):
    return (
        f"\n  {clr(icon + '  ' + title.upper(), BLD + GLD)}\n"
        f"  {clr('─' * 50, GLD)}"
    )

# ── PROMPT ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Eres un consultor experto en transformación digital e implementación de IA en empresas.
Dado un proceso de negocio, identificas oportunidades concretas de automatización con IA.

Responde ÚNICAMENTE en JSON válido con esta estructura exacta, sin texto adicional ni bloques markdown:
{
  "resumen_proceso": "resumen breve en 1-2 frases",
  "oportunidades": [
    {
      "tarea": "nombre corto de la tarea automatizable",
      "problema_actual": "qué falla o es ineficiente ahora",
      "solucion_ia": "qué solución de IA aplicar",
      "herramientas": ["herramienta1", "herramienta2"],
      "impacto_estimado": "impacto concreto: tiempo, coste, errores"
    }
  ],
  "quick_win": "la acción más rápida y fácil de implementar primero",
  "complejidad_implementacion": "baja | media | alta",
  "roi_estimado": "estimación de retorno en tiempo o coste"
}
""".strip()

# ── MODEL SETUP ───────────────────────────────────────────────────────────────
def setup_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(clr("\n  ✗ API Key no encontrada.", RED + BLD))
        print(clr("    Crea un archivo .env con: GEMINI_API_KEY=tu_clave", GRY))
        print(clr("    Obtén tu clave gratuita en: aistudio.google.com\n", GRY))
        sys.exit(1)
    return genai.Client(api_key=api_key)

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
def analizar_proceso(client, descripcion: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nAnaliza este proceso de negocio:\n\n{descripcion}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    texto = response.text.strip()
    if "```" in texto:
        for part in texto.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                texto = part
                break
    return json.loads(texto)

# ── DISPLAY ───────────────────────────────────────────────────────────────────
def wrap(text, width=54, indent="                "):
    lines = textwrap.wrap(str(text), width)
    return ("\n" + indent).join(lines)

def print_report(resultado: dict):
    comp = resultado.get("complejidad_implementacion", "?").lower()
    comp_color = {"baja": GRN, "media": GLD, "alta": RED}.get(comp, WHT)

    print(box("  INFORME DE AUTOMATIZACIÓN CON IA  "))

    print(section_header("📋", "Resumen del proceso"))
    print(f"\n    {clr(wrap(resultado.get('resumen_proceso', '—'), 58, '    '), WHT)}\n")

    print(f"  {clr('⚙', GLD)}   Complejidad :  {clr(comp.upper(), comp_color + BLD)}")
    roi = resultado.get("roi_estimado", "—")
    print(f"  {clr('📈', GLD)}  ROI estimado :  {clr(wrap(roi, 50, '                 '), CYN)}")

    print(section_header("⚡", "Quick win"))
    print(f"\n    {clr(wrap(resultado.get('quick_win', '—'), 58, '    '), GRN + BLD)}\n")

    ops = resultado.get("oportunidades", [])
    print(section_header("🤖", f"Oportunidades detectadas ({len(ops)})"))

    for i, op in enumerate(ops, 1):
        print(f"\n  {clr(str(i) + '.', BLD + GLD)} {clr(op.get('tarea', ''), BLD + WHT)}")
        print(divider(60))
        print(f"    {clr('Problema :   ', GRY)}{wrap(op.get('problema_actual', '—'), 50)}")
        print(f"    {clr('Solución :   ', CYN)}{wrap(op.get('solucion_ia', '—'), 50)}")
        tools = ", ".join(op.get("herramientas", []))
        print(f"    {clr('Stack    :   ', GRY)}{clr(tools, GLD)}")
        print(f"    {clr('Impacto  :   ', GRN)}{wrap(op.get('impacto_estimado', '—'), 50)}")

    print(f"\n{clr('  ' + '═' * 66, GRY)}\n")

# ── INPUT ─────────────────────────────────────────────────────────────────────
def get_input():
    print(section_header("✏", "Descripción del proceso"))
    print(f"\n    {clr('Describe el proceso de negocio que quieres analizar.', GRY)}")
    print(f"    {clr('Incluye: qué se hace, quién lo hace, cuánto tarda y', GRY)}")
    print(f"    {clr('qué problemas tiene. Pulsa Enter dos veces para confirmar.', GRY)}\n")

    lines = []
    print(clr("    › ", GLD), end="", flush=True)
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
        if line != "":
            print(clr("    › ", GLD), end="", flush=True)

    return "\n".join(l for l in lines if l).strip()

# ── SAVE ──────────────────────────────────────────────────────────────────────
def save_output(resultado: dict):
    fname = "resultado_analisis.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print(f"  {clr('✓', GRN)} JSON guardado en {clr(fname, CYN)}\n")

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(box("  Business Process Analyzer  ·  AI Agent Demo  "))
    print(f"  {clr('Christian López Agardi', DIM)}  ·  {clr('christianlxpez.github.io', DIM + CYN)}\n")

    client = setup_client()
    print(f"  {clr('✓', GRN)} Conectado a Gemini 2.5 Flash\n")

    descripcion = get_input()

    if not descripcion:
        print(clr("\n  ✗ No has introducido ningún proceso. Saliendo.\n", RED))
        sys.exit(0)

    print(f"\n  {clr('⟳', GLD)} Analizando proceso con IA...\n")

    try:
        resultado = analizar_proceso(client, descripcion)
        print_report(resultado)
        save_output(resultado)
    except json.JSONDecodeError as e:
        print(clr(f"\n  ✗ Error al parsear JSON: {e}\n", RED))
    except Exception as e:
        print(clr(f"\n  ✗ Error: {e}\n", RED))

if __name__ == "__main__":
    main()
