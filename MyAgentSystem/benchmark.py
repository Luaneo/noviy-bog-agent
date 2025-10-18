#!/usr/bin/env python3
import time, os, json, statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import requests
import pandas as pd
import matplotlib.pyplot as plt

with open('./data/Обращения.txt') as f:
    test_cases = f.readlines()[:25]

url = "http://localhost:8000/question/stream"
messages = []
iterations_per_case = 2
timeout_per_call = 20.0
out_dir = "./data/rag_benchmark_results"
os.makedirs(out_dir, exist_ok=True)


def post_stream(question):
    body = messages + [{"by": "user", "message": question}]
    r = requests.post(url, json=body, stream=True, timeout=(5, None))
    r.raise_for_status()
    parts = []
    chunk_count = 0
    for chunk in r.iter_content(chunk_size=4096):
        if not chunk:
            continue
        chunk_count += 1
        try:
            text = chunk.decode("utf-8", "ignore")
        except Exception:
            text = str(chunk)
        parts.append(text)
    full = "".join(parts)
    print(f"      закончено получение потока, чанков: {chunk_count}, общий размер: {len(full)}")
    return full


def call_with_timeout(func, arg, timeout):
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(func, arg)
        t0 = time.perf_counter()
        try:
            res = fut.result(timeout=timeout)
            return res, None, time.perf_counter() - t0
        except FuturesTimeout:
            return None, TimeoutError(f"timeout after {timeout}s"), time.perf_counter() - t0
        except Exception as e:
            return None, e, time.perf_counter() - t0


results = []
print("Запуск бенчмарка RAG —", datetime.utcnow().isoformat() + "Z")
start_time = datetime.utcnow().isoformat() + "Z"

for qi, q in enumerate(test_cases, start=1):
    print(f"\nВопрос {qi}/{len(test_cases)}: {q}")
    for it in range(1, iterations_per_case + 1):
        print(f"  Итерация {it}/{iterations_per_case}: отправка запроса...")
        try:
            answer, error, elapsed = call_with_timeout(post_stream, q, timeout_per_call)
            if qi == 1:
                continue
            if error is None:
                preview = (answer[:300] + "...") if len(answer) > 300 else answer
                print(f"    ✅ Успех — время: {elapsed:.3f}s, превью ответа: {preview!r}")
                results.append({
                    "question": q,
                    "iteration": it,
                    "elapsed_s": elapsed,
                    "success": True,
                    "error": "",
                    "answer": answer
                })
            else:
                print(f"    ❌ Ошибка: {error} (время: {elapsed:.3f}s)")
                results.append({
                    "question": q,
                    "iteration": it,
                    "elapsed_s": elapsed,
                    "success": False,
                    "error": str(error),
                    "answer": ""
                })
        except Exception as e:
            print(f"    ❌ Внутренняя ошибка: {e}")
            results.append({
                "question": q,
                "iteration": it,
                "elapsed_s": None,
                "success": False,
                "error": f"internal-benchmark-error: {e}",
                "answer": ""
            })
        time.sleep(0.05)

end_time = datetime.utcnow().isoformat() + "Z"
print("\nСбор статистики...")

per_question_summary = []
for q in test_cases:
    times = [r["elapsed_s"] for r in results if
             r["question"] == q and r["success"] and isinstance(r["elapsed_s"], (int, float))]
    errs = [r for r in results if r["question"] == q and not r["success"]]
    answers = [r["answer"] for r in results if r["question"] == q and r["answer"]]
    count = len(times) + len(errs)
    per_question_summary.append({
        "question": q,
        "iterations": count,
        "successes": len(times),
        "failures": len(errs),
        "avg_s": statistics.mean(times) if times else None,
        "median_s": statistics.median(times) if times else None,
        "min_s": min(times) if times else None,
        "max_s": max(times) if times else None,
        "std_s": statistics.stdev(times) if len(times) > 1 else 0.0,
        "sample_answers": answers[:2]
    })

df_calls = pd.DataFrame(results)
df_summary = pd.DataFrame(per_question_summary)
detailed_csv = os.path.join(out_dir, "detailed_calls.csv")
summary_csv = os.path.join(out_dir, "summary.csv")
df_calls.to_csv(detailed_csv, index=False)
df_summary.to_csv(summary_csv, index=False)
print(f"Файлы сохранены: {detailed_csv}, {summary_csv}")

print("Построение графика...")
plt.figure(figsize=(10, 6))
labels = [(q if len(q) <= 40 else q[:37] + "...") for q in df_summary["question"].tolist()]
means = [v if v is not None else 0 for v in df_summary["avg_s"].tolist()]
stds = [v if v is not None else 0 for v in df_summary["std_s"].tolist()]
x = range(len(labels))
plt.errorbar(x, means, yerr=stds, fmt='o', capsize=5)
plt.xticks(x, labels, rotation=30, ha='right')
plt.ylabel("Average response time (s)")
plt.title(f"RAG benchmark — avg response time (iterations={iterations_per_case})")
plt.tight_layout()
plot_path = os.path.join(out_dir, "rag_benchmark.png")
plt.savefig(plot_path)
plt.close()
print(f"График: {plot_path}")

report = {
    "run_started_utc": start_time,
    "run_finished_utc": end_time,
    "iterations_per_question": iterations_per_case,
    "timeout_per_call_s": timeout_per_call,
    "detailed_csv": detailed_csv,
    "summary_csv": summary_csv,
    "plot_png": plot_path
}
with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)

print("\nОтчёт:")
print(f"  start: {report['run_started_utc']}")
print(f"  finish: {report['run_finished_utc']}")
print(f"  iterations_per_question: {report['iterations_per_question']}")
print(f"  timeout_per_call_s: {report['timeout_per_call_s']}")
print(f"  files: {report['detailed_csv']}, {report['summary_csv']}, {report['plot_png']}")

print("\nСводка по вопросам:")
print(df_summary[["question", "avg_s", "median_s", "min_s", "max_s", "std_s", "successes", "failures"]].to_string(
    index=False))

print("\nГотово.")
