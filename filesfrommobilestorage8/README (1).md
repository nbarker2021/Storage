
# SnapLat — Full Build Alpha+ (function-first)

## Quick start
```bash
# run unit tests
pytest -q

# run SnapOps E2E and produce Trails
python -m src.snapops.demo

# run guards
python tools/verify_policy_drift.py policy/snapops_policy.json outputs/policy_hash.json
python tools/verify_beacons_registry.py policy/snapops_policy.json outputs/beacons_hash.json
python tools/verify_component_baseline.py policy/snapops_policy.json policy/beacons.json outputs/components_baseline.json
python tools/verify_fsm_order.py tests/fixtures/trails_fixture.jsonl
```

Artifacts land in `outputs/`.
