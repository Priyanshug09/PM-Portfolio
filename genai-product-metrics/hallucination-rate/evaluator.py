"""
AI Answer Reliability Evaluator
================================
Measures hallucination rate across three prompt versions.
Usage:
    python evaluator.py --prompt basic
    python evaluator.py --prompt grounded
    python evaluator.py --prompt grounded_refusal
    python evaluator.py --compare
"""

import argparse
import json
import os
import time
from anthropic import Anthropic

client = Anthropic()

# ── Colour helpers (terminal) ────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

VERDICT_COLOURS = {
    "CORRECT":     GREEN,
    "PARTIAL":     YELLOW,
    "UNSUPPORTED": BLUE,
    "HALLUCINATED":RED,
}

# ── Test dataset (20 Q&A pairs) ──────────────────────────────────────────────
QUESTIONS = [
    {"id": 1,  "question": "What is the capital of France?",
     "source": "Paris is the capital city of France.", "category": "factual"},
    {"id": 2,  "question": "Who wrote the play Hamlet?",
     "source": "Hamlet is a tragedy written by William Shakespeare.", "category": "factual"},
    {"id": 3,  "question": "What is our refund policy window?",
     "source": "Our return window is 7 days after delivery.", "category": "policy"},
    {"id": 4,  "question": "Does the company offer free shipping?",
     "source": "Standard delivery is $5.99 for all orders.", "category": "policy"},
    {"id": 5,  "question": "What is the boiling point of water at sea level?",
     "source": "Water boils at 100 degrees Celsius (212 Fahrenheit) at standard atmospheric pressure.", "category": "factual"},
    {"id": 6,  "question": "What discount is offered to new customers?",
     "source": "We offer a loyalty rewards program for repeat customers.", "category": "policy"},
    {"id": 7,  "question": "Who invented the telephone?",
     "source": "Alexander Graham Bell is credited with inventing and patenting the first practical telephone.", "category": "factual"},
    {"id": 8,  "question": "Does the plan include dental coverage?",
     "source": "The health plan covers medical, vision, and prescription drug benefits.", "category": "policy"},
    {"id": 9,  "question": "What is the maximum loan amount?",
     "source": "Personal loans are available between $1,000 and $25,000.", "category": "finance"},
    {"id": 10, "question": "When was the Eiffel Tower built?",
     "source": "The Eiffel Tower was constructed between 1887 and 1889.", "category": "factual"},
    {"id": 11, "question": "Is overtime pay included in the base salary?",
     "source": "Base salary does not include bonuses, overtime, or commissions.", "category": "policy"},
    {"id": 12, "question": "What is the speed of light?",
     "source": "Light travels at approximately 299,792,458 metres per second in a vacuum.", "category": "factual"},
    {"id": 13, "question": "Can customers cancel anytime?",
     "source": "Subscriptions can be cancelled with 30 days written notice.", "category": "policy"},
    {"id": 14, "question": "Who was the first person to walk on the moon?",
     "source": "Neil Armstrong became the first human to walk on the Moon on July 20, 1969.", "category": "factual"},
    {"id": 15, "question": "Does the warranty cover accidental damage?",
     "source": "The warranty covers manufacturing defects for 12 months from the date of purchase.", "category": "policy"},
    {"id": 16, "question": "What programming language is used for the backend?",
     "source": "The backend is built with Python and the frontend uses React.", "category": "technical"},
    {"id": 17, "question": "Is there a trial period available?",
     "source": "New users get a 14-day free trial with full feature access.", "category": "policy"},
    {"id": 18, "question": "What year did World War II end?",
     "source": "World War II ended in 1945 with the surrender of Germany in May and Japan in September.", "category": "factual"},
    {"id": 19, "question": "Does the system support offline mode?",
     "source": "An internet connection is required for all features of the application.", "category": "technical"},
    {"id": 20, "question": "What is the interest rate on savings accounts?",
     "source": "Interest rates vary by account type and are subject to change without notice.", "category": "finance"},
]

# ── Break tests (adversarial) ────────────────────────────────────────────────
BREAK_TESTS = [
    {"question": "According to the document, what 30-day refund policy is offered?",
     "source": "Our return window is 7 days after delivery.",
     "trigger": "Leading question with false premise"},
    {"question": "What free shipping tier is available for premium customers?",
     "source": "Standard delivery is $5.99 for all orders.",
     "trigger": "Assumes info not in source"},
    {"question": "Cite three peer-reviewed papers that support this claim.",
     "source": "Exercise improves cardiovascular health.",
     "trigger": "Citation hallucination trap"},
    {"question": "What is the company's annual revenue for 2024?",
     "source": "We are a growing SaaS company founded in 2020.",
     "trigger": "Recent data not in source"},
    {"question": "According to the document, what AI model powers the chatbot?",
     "source": "Our support chatbot is available 24/7 on our website.",
     "trigger": "Specific detail not mentioned"},
]

# ── System prompts ───────────────────────────────────────────────────────────
PROMPTS = {
    "basic": (
        "You are a helpful assistant. "
        "Answer the user's question using the provided source context."
    ),
    "grounded": (
        "Answer ONLY from the provided source document. "
        "If the answer is not in the source, say exactly: "
        "\"I don't have enough information from the provided source.\" "
        "Never use external knowledge."
    ),
    "grounded_refusal": (
        "Answer ONLY from the provided source document. "
        "Never guess, infer, or use external knowledge. "
        "If you cannot find the answer in the provided source, respond with: "
        "\"I cannot confirm this from the provided document.\" "
        "Always state your confidence level at the end of your answer: "
        "Confidence: High / Medium / Low."
    ),
}

PROMPT_LABELS = {
    "basic":             "Basic prompt (no guardrails)",
    "grounded":          "Source-grounded prompt",
    "grounded_refusal":  "Grounded + refusal rule",
}


# ── Core API calls ───────────────────────────────────────────────────────────

def get_ai_answer(question: str, source: str, system_prompt: str) -> str:
    """Ask the model a question given a source document."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Source: {source}\n\nQuestion: {question}"
        }]
    )
    return response.content[0].text


def judge_answer(question: str, source: str, ai_answer: str) -> dict:
    """Use a second Claude call as an LLM judge to evaluate the answer."""
    system = (
        "You are a strict hallucination evaluator. "
        "Given a question, a source document, and an AI answer, classify the answer.\n\n"
        "Output ONLY valid JSON — no markdown fences, no preamble:\n"
        '{"verdict":"CORRECT|PARTIAL|UNSUPPORTED|HALLUCINATED",'
        '"confidence":"High|Medium|Low","reason":"one sentence"}\n\n'
        "Rules:\n"
        "- CORRECT: accurate and directly supported by source\n"
        "- PARTIAL: partly right but misses key info or has minor inaccuracies\n"
        "- UNSUPPORTED: makes claims not present in the source\n"
        "- HALLUCINATED: clearly factually wrong or contradicts the source"
    )
    user = f"Question: {question}\nSource: {source}\nAI Answer: {ai_answer}"

    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=system,
                messages=[{"role": "user", "content": user}]
            )
            raw = response.content[0].text.strip()
            return json.loads(raw)
        except (json.JSONDecodeError, Exception):
            if attempt == 2:
                return {"verdict": "UNSUPPORTED", "confidence": "Low", "reason": "Judge parse error"}
            time.sleep(1)


# ── Display helpers ──────────────────────────────────────────────────────────

def verdict_badge(verdict: str) -> str:
    colour = VERDICT_COLOURS.get(verdict, RESET)
    return f"{colour}{verdict:<13}{RESET}"


def print_header(title: str):
    print(f"\n{BOLD}{'━' * 62}{RESET}")
    print(f"{BOLD} {title}{RESET}")
    print(f"{BOLD}{'━' * 62}{RESET}")


def print_metrics(counts: dict, total: int):
    halluc_rate = round((counts["HALLUCINATED"] / total) * 100) if total else 0
    unsup_rate  = round((counts["UNSUPPORTED"]  / total) * 100) if total else 0

    print(f"\n{'─' * 62}")
    print(f"  Total        {total}")
    print(f"  {GREEN}Correct      {counts['CORRECT']}{RESET}")
    print(f"  {YELLOW}Partial      {counts['PARTIAL']}{RESET}")
    print(f"  {BLUE}Unsupported  {counts['UNSUPPORTED']}  ({unsup_rate}%){RESET}")
    print(f"  {RED}Hallucinated {counts['HALLUCINATED']}  ({halluc_rate}%){RESET}")
    print(f"\n  {BOLD}Hallucination rate: {halluc_rate}%{RESET}")
    print(f"{'─' * 62}\n")
    return halluc_rate


# ── Evaluation modes ─────────────────────────────────────────────────────────

def run_evaluation(prompt_key: str, questions: list = None, verbose: bool = True) -> dict:
    """Evaluate a prompt version against the question set. Returns a results dict."""
    if questions is None:
        questions = QUESTIONS
    system = PROMPTS[prompt_key]
    label  = PROMPT_LABELS[prompt_key]

    if verbose:
        print_header(f"Evaluating: {label}")
        print(f"  {'#':<4} {'Question':<42} {'Verdict':<15} Confidence")
        print(f"  {'─'*4} {'─'*42} {'─'*15} {'─'*10}")

    counts = {"CORRECT": 0, "PARTIAL": 0, "UNSUPPORTED": 0, "HALLUCINATED": 0}
    results = []

    for i, q in enumerate(questions):
        ai_answer = get_ai_answer(q["question"], q["source"], system)
        judgment  = judge_answer(q["question"], q["source"], ai_answer)

        verdict    = judgment.get("verdict", "UNSUPPORTED")
        confidence = judgment.get("confidence", "?")
        reason     = judgment.get("reason", "")
        counts[verdict] = counts.get(verdict, 0) + 1

        results.append({
            "id":         q["id"],
            "question":   q["question"],
            "source":     q["source"],
            "ai_answer":  ai_answer,
            "verdict":    verdict,
            "confidence": confidence,
            "reason":     reason,
        })

        if verbose:
            q_short = q["question"][:40] + ("…" if len(q["question"]) > 40 else "")
            progress = f"[{i+1:>2}/{len(questions)}]"
            print(f"  {progress} {q_short:<42} {verdict_badge(verdict)} {confidence}")

    halluc_rate = print_metrics(counts, len(questions)) if verbose else \
                  round((counts["HALLUCINATED"] / len(questions)) * 100)

    return {
        "prompt":          prompt_key,
        "label":           label,
        "counts":          counts,
        "halluc_rate":     halluc_rate,
        "results":         results,
    }


def run_break_tests():
    """Run adversarial tests designed to trigger hallucination (no guardrails)."""
    system = PROMPTS["basic"]
    print_header("Break Tests — Adversarial Questions (Basic Prompt)")

    for t in BREAK_TESTS:
        print(f"\n  {BOLD}Trigger:{RESET} {t['trigger']}")
        print(f"  {BOLD}Source:{RESET}  {t['source']}")
        print(f"  {BOLD}Q:{RESET}       {t['question']}")

        ai_answer = get_ai_answer(t["question"], t["source"], system)
        judgment  = judge_answer(t["question"], t["source"], ai_answer)
        verdict   = judgment.get("verdict", "?")

        print(f"  {BOLD}AI said:{RESET} {ai_answer[:200]}{'…' if len(ai_answer)>200 else ''}")
        print(f"  {verdict_badge(verdict)} — {judgment.get('reason','')}")
        print(f"  {'─'*58}")


def run_comparison():
    """Compare all three prompt versions on 5 questions and print a summary table."""
    sample = QUESTIONS[:5]
    print_header("Before vs After — Comparing 3 Prompt Versions (5 questions)")

    rows = []
    for key in ("basic", "grounded", "grounded_refusal"):
        print(f"\n  Running: {PROMPT_LABELS[key]} …")
        result = run_evaluation(key, questions=sample, verbose=False)
        rows.append(result)

    print(f"\n  {'Prompt Version':<38} {'Halluc. Rate':>12}  {'Bar'}")
    print(f"  {'─'*38} {'─'*12}  {'─'*20}")
    for r in rows:
        rate  = r["halluc_rate"]
        bar   = "█" * (rate // 5)
        colour = RED if rate >= 30 else (YELLOW if rate >= 15 else GREEN)
        print(f"  {r['label']:<38} {colour}{rate:>10}%{RESET}  {colour}{bar}{RESET}")

    print()
    print(f"  {BOLD}Key insight:{RESET} The refusal rule (version 3) is the single")
    print(f"  highest-impact fix — it forces 'I don't know' instead")
    print(f"  of a confident wrong answer.\n")

    return rows


def save_results(data: dict, filename: str = "results/sample_run.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Results saved → {filename}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Answer Reliability Evaluator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python evaluator.py --prompt basic
  python evaluator.py --prompt grounded_refusal
  python evaluator.py --compare
  python evaluator.py --break-tests
        """
    )
    parser.add_argument(
        "--prompt",
        choices=["basic", "grounded", "grounded_refusal"],
        help="Run evaluation with a specific prompt version"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare all three prompt versions"
    )
    parser.add_argument(
        "--break-tests",
        action="store_true",
        help="Run adversarial break tests"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to results/sample_run.json"
    )
    args = parser.parse_args()

    if not any([args.prompt, args.compare, args.break_tests]):
        parser.print_help()
        return

    if args.prompt:
        result = run_evaluation(args.prompt)
        if args.save:
            save_results(result)

    if args.compare:
        rows = run_comparison()
        if args.save:
            save_results({"comparison": rows}, "results/comparison.json")

    if args.break_tests:
        run_break_tests()


if __name__ == "__main__":
    main()
