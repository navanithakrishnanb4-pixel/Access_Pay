"""Payment Truth Layer PoC  -  version 1.0  (rule-based risk + four renderers).
Synthetic data only. No real payments, accounts, or biometrics."""
import re
VERSION = "1.0"

def inr(n):
    """Indian digit grouping: 1250000 -> 12,50,000"""
    s = str(int(n)); 
    if len(s) <= 3: return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
    if head: parts.insert(0, head)
    return ",".join(parts + [tail])

URGENCY = ["urgent","immediately","blocked","suspended","disconnected","within 24 hours","last chance","pay now","tonight","today only"]
FEE_PATTERNS = ["to verify","processing fee","registration fee","to receive","refund","prize","lottery","kyc","customs","insurance fee","advance","release your claim","guaranteed","cashback","pay tax"]
IMPERSONATION = ["bank","customer care","officer","police","rbi","helpline","tech support","calling from"]

def build_record(c):
    """Single verified record  (WHO / HOW MUCH / WHAT / RISK / WHY)."""
    name = (c.get("payee_name") or "").strip()
    amt_raw = (c.get("amount") or "").strip()
    try:
        amt = float(amt_raw) if amt_raw != "" else None
    except ValueError:
        amt = None
    rec = {"case_id": c["case_id"], "who": name, "upi": c.get("payee_upi",""), "how_much": None if amt is None else int(amt),
           "what": f"UPI payment via {c.get('channel','UPI_ID').replace('_',' ').lower()}", "risk": None, "why": [], "state": "OK"}
    if not name or amt is None or amt <= 0:
        rec["state"] = "UNCERTAIN"; rec["risk"] = "UNCERTAIN"
        rec["why"] = ["Payee or amount could not be verified. Check with the payee or your bank before paying."]
        return rec
    msg = (c.get("message") or "").lower()
    saved = c.get("saved_contact_upi",""); typical = c.get("typical_amount","")
    score = 0; why = []
    new_payee = (saved == "")
    if new_payee and c.get("typical_amount","") == "" and c.get("channel") != "QR":
        score += 2; why.append("Recipient is new to you")
    elif new_payee and c.get("channel") == "QR":
        pass
    if saved and c["payee_upi"] != saved:
        score += 3; why.append("Payment ID differs from the saved contact")
    if typical:
        if amt > 5*float(typical): score += 2; why.append("Amount is much higher than usual")
    elif new_payee and amt >= 10000:
        score += 2; why.append("Large amount to a new recipient")
    if any(k in msg for k in URGENCY): score += 3; why.append("Message uses urgency or threat")
    if any(k in msg for k in FEE_PATTERNS): score += 3; why.append("Message asks for a fee, advance or verification payment")
    if c.get("channel") == "COLLECT_REQUEST": score += 3; why.append("This is a request that takes money from you")
    qm = (c.get("qr_merchant_name") or "").strip()
    if c.get("channel") == "QR" and qm and qm.lower() != name.lower(): score += 3; why.append("QR shop name does not match the payee name")
    if new_payee and any(k in msg for k in IMPERSONATION): score += 3; why.append("Message claims to be a bank or official")
    rec["risk"] = "HIGH" if score >= 6 else ("MEDIUM" if score >= 3 else "LOW")
    rec["why"] = why if why else ["No unusual signs found"]
    rec["score"] = score
    return rec

HAPTIC = {"LOW": "1 short pulse", "MEDIUM": "2 long pulses", "HIGH": "3 long pulses + 1 short", "UNCERTAIN": "continuous pulse 2 s"}
HAPTIC_CONFIRM = "2 short pulses"; HAPTIC_CANCEL = "1 long pulse"

def render_screen_reader(r):
    amt = "amount not verified" if r["how_much"] is None else f"{inr(r['how_much'])} rupees"
    who = r["who"] or "unverified recipient"
    if r["risk"] == "UNCERTAIN":
        return f"Uncertain. You are paying {who}, {amt}. {r['why'][0]}"
    return f"{r['risk'].capitalize()} risk. You are paying {inr(r['how_much'])} rupees to {who}. Reason: {r['why'][0]}."

def render_visual(r):
    amt = "?" if r["how_much"] is None else f"₹{inr(r['how_much'])}"
    return f"{r['risk']} RISK | {amt} → {r['who'] or 'UNVERIFIED'} | Reason: {r['why'][0]}"

def render_simple(r):
    head = {"HIGH":"STOP.","MEDIUM":"CHECK.","LOW":"OK.","UNCERTAIN":"WAIT."}[r["risk"]]
    amt = "?" if r["how_much"] is None else f"₹{inr(r['how_much'])}"
    return f"{head} {r['risk']}. {amt} to {r['who'] or 'UNVERIFIED'}. {r['why'][0]}"

def render_haptic(r): return HAPTIC[r["risk"]]

def render_all(r):
    return {"screen_reader": render_screen_reader(r), "visual": render_visual(r), "simple": render_simple(r), "haptic": render_haptic(r)}

# ---------- independent consistency checker (parses OUTPUT text, not the record) ----------
def parse_amount(text):
    m = re.search(r"(?:₹|)\s?([0-9][0-9,]*)\s?(?:rupees)?", text)
    return int(m.group(1).replace(",","")) if m else None

def check_consistency(rec, outs):
    """Pre-registered rule: audio/visual/simple must carry payee, amount, risk word and the first reason;
    haptic must carry the risk level only (pattern id)."""
    fails = []
    for mode in ("screen_reader","visual","simple"):
        t = outs[mode]
        if rec["who"] and rec["who"] not in t: fails.append(f"{mode}: payee missing")
        if rec["how_much"] is not None and str(rec["how_much"]) not in re.sub(r"[,₹ ]","",t): fails.append(f"{mode}: amount missing")
        if rec["risk"].lower() not in t.lower(): fails.append(f"{mode}: risk missing")
        if rec["why"][0].rstrip(".").lower() not in t.lower(): fails.append(f"{mode}: reason missing")
    if outs["haptic"] != HAPTIC[rec["risk"]]: fails.append("haptic: pattern mismatch")
    return fails
