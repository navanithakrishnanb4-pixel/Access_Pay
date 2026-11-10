# Calculations (from runs/*_summary.json)
| Run | Version | Cases file | T1 consistent | Recall (risky flagged / 20) | False alerts (safe flagged / 20) | Amount-only baseline recall / false alerts | Median ms | p95 ms | Role |
|-----|---------|-----------|---------------|------------------------------|-----------------------------------|------------------------------|-----------|--------|------|
| R01 | 1.0 | set A | 40/40 | 20/20 (100%) | 0/20 (0%) | 11/20 ; 4/20 | 0.0089 | 0.0098 | development set (optimistic) |
| R02 | 1.0 | set B | 40/40 | 10/20 (50%) | 4/20 (20%) | 8/20 ; 4/20 | 0.0124 | 0.0140 | fresh holdout for v1.0 -> GAP, stop rule (recall < 70%) |
| R03 | 1.1 | set C | 40/40 | 16/20 (80%) | 2/20 (10%) | 8/20 ; 3/20 | 0.0113 | 0.0272 | fresh holdout for v1.1 -> recall below 85%; false-alert limit met |
| R04 | 1.1 | set A | 40/40 | 20/20 | 0/20 | 11/20 ; 4/20 | 0.0125 | 0.0154 | regression only |
| R05 | 1.1 | set B | 40/40 | 19/20 | 3/20 | 8/20 ; 4/20 | 0.0120 | 0.0144 | regression only (tuned on these cases) |
Boundary cases B01-B06 (missing payee, missing amount, negative amount, very long name, Tamil-script name, Rs 1 crore): 6/6 met expectation in v1.0 and v1.1.
R02 misses: R21 R23 R27 R28 R31 R35 R36 R38 R39 R40. R02 false alerts: S24 S25 S32 S39.
R03 misses: R52 R54 R58 R60. R03 false alerts: S50 S58.
Technical outcome: PARTLY SUPPORTED (T1 and T3 met on synthetic data; T2 recall 16/20 = 80% < 85% on fresh set C; false alerts 2/20 = 10% met).
