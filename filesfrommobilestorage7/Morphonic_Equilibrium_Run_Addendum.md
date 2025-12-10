# Run Addendum — Morphonic Equilibrium (Harness results)

**Harness:** `unibeam_dualrail_harness.py` (dim=128, fam=32, steps=40×2 rails)

## Closure Certificate
```json
{
  "idf_equal": false,
  "sum_delta_phi_forward": -0.28852647449821234,
  "sum_delta_phi_adjoint": -0.2684649210423231,
  "reality": false
}
```

## Receipt samples (first 10)
```json
[
  {
    "step": 1,
    "rail": "forward",
    "tri": {
      "witness_ids": [
        "ddbdd0f6",
        "21f18d2c",
        "ca4a83c4"
      ],
      "pose_residual": 1.5951384177360457,
      "rank": 0.9815936753841906
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.020000819116830826
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.010000409558415413,
      "dLandauer": 0.0
    },
    "delta_phi": -0.010000409558415413,
    "outcome": "refuse"
  },
  {
    "step": 1,
    "rail": "adjoint",
    "tri": {
      "witness_ids": [
        "3ff13ece",
        "934d7345",
        "5bea7238"
      ],
      "pose_residual": 1.651959570868843,
      "rank": 0.9164626299858888
    },
    "quad": {
      "used": true,
      "chosen": 0,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": true,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.0
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.0,
      "dLandauer": 0.0
    },
    "delta_phi": 0.0,
    "outcome": "commit"
  },
  {
    "step": 2,
    "rail": "forward",
    "tri": {
      "witness_ids": [
        "3fe514be",
        "7ccaae2a",
        "abeb41ad"
      ],
      "pose_residual": 1.5530136774822547,
      "rank": 0.9373969880676145
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.01982341893017292
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.00991170946508646,
      "dLandauer": 0.0
    },
    "delta_phi": -0.00991170946508646,
    "outcome": "refuse"
  },
  {
    "step": 2,
    "rail": "adjoint",
    "tri": {
      "witness_ids": [
        "36c1f1b2",
        "657f717b",
        "3873bd31"
      ],
      "pose_residual": 1.6135730963841648,
      "rank": 0.9739264465964831
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.019955696538090706
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.009977848269045353,
      "dLandauer": 0.0
    },
    "delta_phi": -0.009977848269045353,
    "outcome": "refuse"
  },
  {
    "step": 3,
    "rail": "forward",
    "tri": {
      "witness_ids": [
        "65126766",
        "f5d1ca72",
        "3418d086"
      ],
      "pose_residual": 1.553050891553262,
      "rank": 0.9361030518699843
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.019974272698163986
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.009987136349081993,
      "dLandauer": 0.0
    },
    "delta_phi": -0.009987136349081993,
    "outcome": "refuse"
  },
  {
    "step": 3,
    "rail": "adjoint",
    "tri": {
      "witness_ids": [
        "b0aa228b",
        "a2bf06f0",
        "8a53fa87"
      ],
      "pose_residual": 1.493373906417812,
      "rank": 0.9543854432398142
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.019941747188568115
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.009970873594284058,
      "dLandauer": 0.0
    },
    "delta_phi": -0.009970873594284058,
    "outcome": "refuse"
  },
  {
    "step": 4,
    "rail": "forward",
    "tri": {
      "witness_ids": [
        "8905b511",
        "0c76237e",
        "16e87d6b"
      ],
      "pose_residual": 1.6029470749996824,
      "rank": 0.9183049126915296
    },
    "quad": {
      "used": true,
      "chosen": 0,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": true,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.0
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.0,
      "dLandauer": 0.0
    },
    "delta_phi": 0.0,
    "outcome": "commit"
  },
  {
    "step": 4,
    "rail": "adjoint",
    "tri": {
      "witness_ids": [
        "4f6a1f60",
        "16e3e1ba",
        "3c5cda21"
      ],
      "pose_residual": 1.5906503121977544,
      "rank": 0.9115760383045324
    },
    "quad": {
      "used": true,
      "chosen": 0,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": true,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.0
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.0,
      "dLandauer": 0.0
    },
    "delta_phi": 0.0,
    "outcome": "commit"
  },
  {
    "step": 5,
    "rail": "forward",
    "tri": {
      "witness_ids": [
        "76090561",
        "341ab664",
        "45377f98"
      ],
      "pose_residual": 1.5735447674809668,
      "rank": 0.9519476653389835
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.019961634650826454
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.009980817325413227,
      "dLandauer": 0.0
    },
    "delta_phi": -0.009980817325413227,
    "outcome": "refuse"
  },
  {
    "step": 5,
    "rail": "adjoint",
    "tri": {
      "witness_ids": [
        "e26a1646",
        "ea66cc47",
        "18f62633"
      ],
      "pose_residual": 1.5998086175086041,
      "rank": 0.9653626478752235
    },
    "quad": {
      "used": false,
      "chosen": null,
      "delta_phi_gain": 0.0
    },
    "idf": {
      "equal": false,
      "hash": "6ecee83c40de2088abb94a09f743899539c00e43117b444a64e5f7f0fb85e746"
    },
    "errs": {
      "err_proxy": 0.019990328699350357
    },
    "sectors": {
      "dNoether": 0.0,
      "dShannon": -0.009995164349675179,
      "dLandauer": 0.0
    },
    "delta_phi": -0.009995164349675179,
    "outcome": "refuse"
  }
]
```

### Notes
- Identity family equality across steps: False
- Total Δφ (forward + adjoint): -0.556991
- Reality verdict: False
- See full logs in: `unibeam_receipts.jsonl` and `harness_run.log`.
