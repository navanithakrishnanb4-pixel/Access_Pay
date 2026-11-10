# Frozen test card  DPPD-T01
Carried forward unchanged from P2 Slide 10 (smallest PoC). Unit of analysis: one synthetic payment case. Planned 40 per run.
| ID | Measure | Comparator / reference | Original criterion |
|----|---------|------------------------|--------------------|
| T1 | Consistency of payee, amount, risk, reason across 4 outputs (parsed from output text) | Manual check of same cases (NOT TESTED) | 40/40 consistent |
| T2 | Rule-based risk labels: recall on 20 risky cases; false alerts on 20 safe cases (flag = MEDIUM or HIGH) | Labels agreed before rules; baseline = amount-only rule (flag if amount >= 5,000) | recall >= 85% (>=17/20); false alerts <= 10% (<=2/20) |
| T3 | Time to build record + render 4 outputs (ms, median and p95; 20 in-process repeats per case) | Manual: NOT TESTED | < 1 s per record |
Stop rule (P2): stop / simplify and repeat if < 36/40 consistent, or recall < 70%, or false alerts > 20%.
## Change log (nothing relaxed)
- C1 (definition clarification, in the checker before R01): haptic output carries the risk level only; audio, visual and simple outputs carry payee, amount, risk and first reason. UNCERTAIN state is rendered when payee/amount cannot be verified.
- C2 (artifact change after R02): rules v1.0 -> v1.1 (micro-payment, pay/send-request, emergency-story rules; reduced weight of urgency/fee words for a saved contact with same ID and normal amount; -1 when link merchant name equals payee). Thresholds unchanged. Retest on FRESH set C. Sets A and B reused only as regression.
