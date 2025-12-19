python - <<'PY'
import pathlib, re
p = pathlib.Path("shared/evals/runner.py")
t = p.read_text()

# Replace ONLY the metrics_contains block in _evaluate_meeting_followup
pattern = r'if "metrics_contains" in ex:\n\s*for item in ex\["metrics_contains"\]:\n\s*msg = assert_contains\(extracted, item, f"metrics contains \{item\}"\)\n\s*if msg: failures.append\(msg\)\n'
replacement = '''if "metrics_contains" in ex:
        metrics = extracted.get("metrics", []) or []
        for item in ex["metrics_contains"]:
            msg = assert_contains(metrics, item, f"metrics contains {item}")
            if msg: failures.append(msg)
'''
new = re.sub(pattern, replacement, t, flags=re.MULTILINE)
p.write_text(new)
print("patched shared/evals/runner.py metrics_contains")
PY
