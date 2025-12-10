
.PHONY: test e2e guards package ci-local

test:
	pytest -q

e2e:
	python -m src.snapops.demo

guards:
	python tools/verify_policy_drift.py policy/snapops_policy.json outputs/policy_hash.json
	python tools/verify_beacons_registry.py policy/snapops_policy.json outputs/beacons_hash.json
	python tools/verify_component_baseline.py policy/snapops_policy.json policy/beacons.json outputs/components_baseline.json
	python tools/verify_fsm_order.py tests/fixtures/trails_fixture.jsonl

package:
	zip -r SnapLat_FullBuild_AlphaPlus.zip . -x "*/__pycache__/*"

ci-local: test e2e guards
