"""
Business Process Analyzer — AI Agent Demo
Christian López Agardi · christianlxpez.github.io

Analyzes a business process and identifies AI automation
opportunities using Google Gemini (free tier).

SETUP:
  1. pip install google-genai python-dotenv
  2. Create a .env file with:  GEMINI_API_KEY=AIza...
     (or: export GEMINI_API_KEY=AIza...)
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
    print("\n  ✗ Install: pip install google-genai python-dotenv\n")
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
PRP = "\033[38;5;183m"

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

# ── EXAMPLE PROCESSES ────────────────────────────────────────────────────────
EXAMPLES = [
    {
        "label": "Invoice processing",
        "company": "Distribution company",
        "text": (
            "A distribution company receives around 300 supplier invoices per week via email "
            "as PDF attachments. An admin manually opens each PDF, extracts the key fields "
            "(supplier name, amount, due date, invoice number), types them into an Excel sheet, "
            "then uploads the data to their ERP system. The process takes 3 full working days per "
            "week, errors are frequent due to manual entry, and invoices sometimes get lost or "
            "processed late, causing payment delays and supplier complaints."
        )
    },
    {
        "label": "Customer support inbox",
        "company": "E-commerce brand",
        "text": (
            "An e-commerce company handles over 500 customer support emails per day. Staff manually "
            "reads each email, categorizes it (returns, shipping issues, billing, complaints, general "
            "questions), assigns it to the right team member, and drafts a reply. 70% of the emails "
            "are repetitive and follow the same patterns. Average first response time is 48 hours. "
            "The team of 6 agents spends most of their day on low-value repetitive tasks instead of "
            "handling complex cases that actually require human judgment."
        )
    },
    {
        "label": "Sales lead qualification",
        "company": "B2B SaaS startup",
        "text": (
            "A B2B SaaS startup gets around 150 inbound leads per week through their website contact "
            "form and LinkedIn. A sales rep manually visits each lead's LinkedIn profile and company "
            "website, researches their size, industry and tech stack, decides if they fit the ICP "
            "(Ideal Customer Profile), writes a personalized first outreach email, and logs everything "
            "in the CRM. Each lead takes 20-30 minutes to research and contact. The sales team misses "
            "many leads due to time constraints and follow-ups are inconsistent."
        )
    }
]

# ── PROMPT ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert consultant in AI implementation and digital transformation for businesses.
Given a description of a business process, you identify specific, actionable automation opportunities using modern AI tools.

Be as specific as possible with tool recommendations — name real products:
- For workflow automation: n8n, Make (Integromat), Zapier
- For AI agents: LangChain, LlamaIndex, CrewAI, AutoGen
- For LLMs: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro (name the specific model)
- For document/data extraction: Gemini Vision, Mistral OCR, Mindee, Amazon Textract
- For email/communication: Gmail API, Microsoft Graph API, Resend
- For NLP classification: fine-tuned BERT, zero-shot classification with Claude, OpenAI function calling
- For databases: Airtable, Supabase, Notion API, PostgreSQL
- For CRM integration: HubSpot API, Salesforce API, Pipedrive

Return ONLY valid JSON with this exact structure, no markdown, no extra text:
{
  "process_summary": "1-2 sentence summary of the process and its main problems",
  "opportunities": [
    {
      "task": "short name of the automatable task",
      "current_problem": "what is inefficient or broken right now",
      "ai_solution": "specific solution with named tools and how they connect",
      "stack": ["Tool1", "Tool2", "Tool3"],
      "estimated_impact": "concrete impact: time saved, error reduction, cost"
    }
  ],
  "quick_win": "the fastest, easiest thing to implement first — with specific tool",
  "implementation_complexity": "low | medium | high",
  "estimated_roi": "concrete time or cost return estimate"
}
""".strip()

# ── MODEL SETUP ───────────────────────────────────────────────────────────────
def setup_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(clr("\n  ✗ API Key not found.", RED + BLD))
        print(clr("    Create a .env file with: GEMINI_API_KEY=your_key", GRY))
        print(clr("    Get your free key at: aistudio.google.com\n", GRY))
        sys.exit(1)
    return genai.Client(api_key=api_key)

# ── ANALYSIS ──────────────────────────────────────────────────────────────────
def analyze_process(client, description: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nAnalyze this business process:\n\n{description}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    text = response.text.strip()
    if "```" in text:
        for part in text.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                text = part
                break
    return json.loads(text)

# ── DISPLAY ───────────────────────────────────────────────────────────────────
def wrap(text, width=54, indent="                "):
    lines = textwrap.wrap(str(text), width)
    return ("\n" + indent).join(lines)

def print_report(result: dict):
    comp = result.get("implementation_complexity", "?").lower()
    comp_color = {"low": GRN, "medium": GLD, "high": RED}.get(comp, WHT)

    print(box("  AUTOMATION ANALYSIS REPORT  "))

    # Summary
    print(section_header("📋", "Process summary"))
    print(f"\n    {clr(wrap(result.get('process_summary', '—'), 58, '    '), WHT)}\n")

    # Metrics
    print(f"  {clr('⚙', GLD)}   Complexity   :  {clr(comp.upper(), comp_color + BLD)}")
    roi = result.get("estimated_roi", "—")
    print(f"  {clr('📈', GLD)}  Estimated ROI :  {clr(wrap(roi, 50, '                  '), CYN)}")

    # Quick win
    print(section_header("⚡", "Quick win"))
    print(f"\n    {clr(wrap(result.get('quick_win', '—'), 58, '    '), GRN + BLD)}\n")

    # Opportunities
    ops = result.get("opportunities", [])
    print(section_header("🤖", f"Automation opportunities ({len(ops)})"))

    for i, op in enumerate(ops, 1):
        print(f"\n  {clr(str(i) + '.', BLD + GLD)} {clr(op.get('task', ''), BLD + WHT)}")
        print(divider(60))
        print(f"    {clr('Problem  :   ', GRY)}{wrap(op.get('current_problem', '—'), 50)}")
        print(f"    {clr('Solution :   ', CYN)}{wrap(op.get('ai_solution', '—'), 50)}")
        stack = ", ".join(op.get("stack", []))
        print(f"    {clr('Stack    :   ', GRY)}{clr(stack, GLD)}")
        print(f"    {clr('Impact   :   ', GRN)}{wrap(op.get('estimated_impact', '—'), 50)}")

    print(f"\n{clr('  ' + '═' * 66, GRY)}\n")

# ── MENU ──────────────────────────────────────────────────────────────────────
def show_menu():
    print(section_header("📂", "Choose a process to analyze"))
    print(f"\n    {clr('Select one of the examples below or enter your own:', GRY)}\n")

    for i, ex in enumerate(EXAMPLES, 1):
        print(f"  {clr(f'  [{i}]', BLD + GLD)}  {clr(ex['label'], WHT)}  {clr('— ' + ex['company'], GRY)}")

    print(f"\n  {clr('  [4]', BLD + PRP)}  {clr('Enter your own process description', WHT)}\n")
    print(clr("    › Choose (1-4): ", GLD), end="", flush=True)

    while True:
        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if choice in ("1", "2", "3"):
            idx = int(choice) - 1
            ex = EXAMPLES[idx]
            print(f"\n  {clr('✓', GRN)} Selected: {clr(ex['label'], WHT)}\n")
            print(f"  {clr('Process description:', GRY)}")
            for line in textwrap.wrap(ex["text"], 66):
                print(f"    {clr(line, DIM)}")
            print()
            return ex["text"]
        elif choice == "4":
            return get_custom_input()
        else:
            print(clr("    › Invalid choice. Enter 1, 2, 3 or 4: ", RED), end="", flush=True)

def get_custom_input():
    print(section_header("✏", "Describe your process"))
    print(f"\n    {clr('Describe the business process you want to analyze.', GRY)}")
    print(f"    {clr('Include: what is done, who does it, how long it takes,', GRY)}")
    print(f"    {clr('and what problems it has. Press Enter twice to confirm.', GRY)}\n")

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
def save_output(result: dict):
    fname = "analysis_output.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  {clr('✓', GRN)} JSON saved to {clr(fname, CYN)}\n")

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print(box("  Business Process Analyzer  ·  AI Agent Demo  "))
    print(f"  {clr('Christian López Agardi', DIM)}  ·  {clr('christianlxpez.github.io', DIM + CYN)}\n")

    client = setup_client()
    print(f"  {clr('✓', GRN)} Connected to Gemini 2.5 Flash\n")

    description = show_menu()

    if not description:
        print(clr("\n  ✗ No process entered. Exiting.\n", RED))
        sys.exit(0)

    print(f"\n  {clr('⟳', GLD)} Analyzing process with AI...\n")

    try:
        result = analyze_process(client, description)
        print_report(result)
        save_output(result)
    except json.JSONDecodeError as e:
        print(clr(f"\n  ✗ JSON parse error: {e}\n", RED))
    except Exception as e:
        print(clr(f"\n  ✗ Error: {e}\n", RED))

if __name__ == "__main__":
    main()
