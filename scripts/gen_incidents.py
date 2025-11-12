# scripts/gen_incidents.py
"""
Phase 1: Synthetic Troubleshooting Document Generation

Generates:
 - 50 incidents for customer-service
 - 50 incidents for product-service
 - 50 incidents for order-service
 - 10 cross-cutting incidents

Writes output to: data/incidents.jsonl
(one JSON object per line)
"""

import json
import uuid
import random
from datetime import datetime, timezone

# === CONFIG - change these only if you want different counts ===
PER_SERVICE = 50      # assignment requires 50
CROSS_CUTTING = 10    # assignment requires 10
OUTPATH = "data/incidents.jsonl"
# ===============================================================

SERVICES = ["customer-service", "product-service", "order-service"]
SHORT_SYMPTOMS = [
    "timeout on request",
    "incorrect data returned",
    "payment failure",
    "auth error",
    "inventory mismatch",
    "order duplication",
    "slow response",
    "500 internal error",
    "missing records",
    "cache inconsistency"
]
ROOT_CAUSES = [
    "downstream service timeout",
    "schema mismatch",
    "race condition in order handler",
    "missing null-check",
    "stale cache causing mismatch",
    "misconfigured retry policy",
    "DB deadlock",
    "faulty deployment",
    "incorrect validation logic",
    "circumstantial network partition"
]
FIXES = [
    "added retry with exponential backoff",
    "fixed null-check and added unit test",
    "rolled back faulty deploy",
    "increased DB connection pool size",
    "invalidated cache and added cache versioning",
    "patched validation and added input sanitization",
    "implemented idempotency for requests",
    "added monitoring and alerting for thresholds",
    "migrated to stronger transaction isolation",
    "applied hotfix and scheduled full rollout"
]

ERROR_CODES = ["E100","E201","E305","E412","E520","E611","E722","E833","E944","E055"]

def unique_title(base_set, candidate):
    """Ensure the title is unique in base_set; if not, append suffix"""
    title = candidate
    i = 1
    while title in base_set:
        i += 1
        title = f"{candidate} - {i}"
    base_set.add(title)
    return title

def make_incident(service, used_titles):
    iid = str(uuid.uuid4())
    symptom = random.choice(SHORT_SYMPTOMS)
    error = random.choice(ERROR_CODES)
    title_base = f"{service} - {symptom} - {error}"
    title = unique_title(used_titles, title_base)
    description = (
        f"Observed symptom: {symptom}. "
        f"Users reported failures in the {service} during normal operations. "
        f"Logs show patterns of {random.choice(['timeouts','500 responses','db errors','auth failures','exceptions'])} "
        f"on related endpoints. Example log snippet: \"{error}: {symptom} at handler\"."
    )
    root_cause = random.choice(ROOT_CAUSES)
    fixes_applied = random.choice(FIXES)
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "id": iid,
        "service": service,
        "title": title,
        "description": description,
        "root_cause": root_cause,
        "fixes_applied": fixes_applied,
        "timestamp": timestamp
    }

def make_cross_cutting(i, used_titles):
    iid = str(uuid.uuid4())
    title_base = f"cross-cutting - transactional inconsistency - CC{i+1}"
    title = unique_title(used_titles, title_base)
    description = (
        "This incident spans multiple services (customer-service, order-service, product-service). "
        "Symptom: inconsistent order state across services, failed compensating transactions, and user-visible errors."
    )
    root_cause = "transactional inconsistency across services / missing compensation flow"
    fixes_applied = "introduced compensation transaction, added distributed tracing and retries, added end-to-end tests"
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "id": iid,
        "service": "cross-cutting",
        "title": title,
        "description": description,
        "root_cause": root_cause,
        "fixes_applied": fixes_applied,
        "timestamp": timestamp
    }

def main():
    used_titles = set()
    out = []

    # Per-service incidents
    for svc in SERVICES:
        for _ in range(PER_SERVICE):
            out.append(make_incident(svc, used_titles))

    # Cross-cutting incidents
    for i in range(CROSS_CUTTING):
        out.append(make_cross_cutting(i, used_titles))

    # Write to JSONL
    with open(OUTPATH, "w", encoding="utf-8") as f:
        for item in out:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(out)} incidents to {OUTPATH}")

if __name__ == "__main__":
    main()
