import csv, json, sys, time, hashlib, platform, statistics, datetime
import importlib, os
MOD=sys.argv[3] if len(sys.argv)>3 else 'truth_layer'
_m=importlib.import_module(MOD)
build_record,render_all,check_consistency,VERSION=_m.build_record,_m.render_all,_m.check_consistency,_m.VERSION
def load(p): return list(csv.DictReader(open(p, encoding="utf-8")))
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()[:16]
run_id, cases_file = sys.argv[1], sys.argv[2]
cases = load(cases_file); results = []; times = []
for c in cases:
    t0 = [];
    for _ in range(20):
        a = time.perf_counter(); r = build_record(c); o = render_all(r); t0.append((time.perf_counter()-a)*1000)
    fails = check_consistency(r, o)
    flagged = r["risk"] in ("MEDIUM","HIGH")
    amt_only = (float(c["amount"]) >= 5000) if c.get("amount") not in ("",None) and float(c["amount"])>0 else False
    results.append({"case_id": c["case_id"], "label": c.get("label",""), "risk": r["risk"], "flagged": flagged, "amount_only_flag": amt_only,
                    "consistent": not fails, "fail_detail": "; ".join(fails), "reasons": " | ".join(r["why"]), "median_ms": round(statistics.median(t0),4)})
    times.append(statistics.median(t0))
def counts(rs, key):
    risky=[x for x in rs if x["label"]=="RISKY"]; safe=[x for x in rs if x["label"]=="SAFE"]
    return {"risky_total":len(risky),"risky_flagged":sum(x[key] for x in risky),"safe_total":len(safe),"safe_flagged":sum(x[key] for x in safe)}
lab=[x for x in results if x["label"] in ("RISKY","SAFE")]
summary = {"run_id":run_id,"truth_layer_version":VERSION,"python":platform.python_version(),"date_utc":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M"),
  "cases_file":cases_file,"module":MOD,"cases_sha256_16":sha(cases_file),"code_sha256_16":sha(MOD+".py"),"n_cases":len(results),
  "T1_consistent":sum(x["consistent"] for x in results),"T1_total":len(results),
  "T2_rules":counts(lab,"flagged"),"T2_amount_only_baseline":counts(lab,"amount_only_flag"),
  "T2_uncertain_count":sum(x["risk"]=="UNCERTAIN" for x in lab),
  "T3_median_ms":round(statistics.median(times),4),"T3_p95_ms":round(sorted(times)[int(0.95*len(times))-1],4),"T3_max_ms":round(max(times),4)}
json.dump(summary, open(f"runs/{run_id}_summary.json","w"), indent=1)
with open(f"runs/{run_id}_cases.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)
print(json.dumps(summary, indent=1))
for x in results:
    if x["label"]=="RISKY" and not x["flagged"]: print("MISSED RISKY:",x["case_id"],x["risk"],x["reasons"])
    if x["label"]=="SAFE" and x["flagged"]: print("FALSE ALERT:",x["case_id"],x["risk"],x["reasons"])
    if not x["consistent"]: print("INCONSISTENT:",x["case_id"],x["fail_detail"])
