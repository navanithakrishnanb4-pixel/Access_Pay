import csv, sys, importlib, json
MOD = sys.argv[1] if len(sys.argv) > 1 else "truth_layer"
m = importlib.import_module(MOD)
rows = list(csv.DictReader(open("data/boundary_cases.csv", encoding="utf-8")))
out = []
for c in rows:
    try:
        r = m.build_record(c); o = m.render_all(r); f = m.check_consistency(r, o)
        ok_expect = {"UNCERTAIN": r["risk"] == "UNCERTAIN"}.get(c["expected_behaviour"], True) and not f
        out.append({"case_id": c["case_id"], "expected": c["expected_behaviour"], "risk": r["risk"], "consistent": not f, "met_expectation": ok_expect, "detail": "; ".join(f), "screen_reader": o["screen_reader"]})
    except Exception as e:
        out.append({"case_id": c["case_id"], "expected": c["expected_behaviour"], "risk": "ERROR", "consistent": False, "met_expectation": False, "detail": repr(e), "screen_reader": ""})
w = csv.DictWriter(open(f"runs/boundary_{MOD}.csv", "w", newline="", encoding="utf-8"), fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for x in out: print(x["case_id"], x["expected"], "->", x["risk"], "| consistent:", x["consistent"], "| met:", x["met_expectation"], x["detail"])
print("met expectation:", sum(x["met_expectation"] for x in out), "/", len(out))
