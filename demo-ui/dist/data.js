window.lab9 = {
  "ticketDays": 5,
  "runs": {
    "seeded_regression": {
      "events": [
        {
          "kind": "handoff",
          "payload": {
            "allowed_tools": [
              "lookup_order",
              "lookup_policy",
              "compute_compensation"
            ],
            "max_output_tokens": 400,
            "contract_version": "handoff.v1",
            "request_id": "REQ-C-002",
            "principal_scope": "owner_order_only",
            "task": "check_applicable_policy",
            "facts": {},
            "claim_id": "C-002"
          }
        },
        {
          "kind": "investigator",
          "payload": {
            "lookup_order": {
              "visible": true,
              "reason": "ok",
              "order": {
                "order_id": "O-202",
                "status": "delivered",
                "delay_days": 2,
                "shipping_fee_vnd": 20000,
                "paid_vnd": 100000,
                "damage_verified": false,
                "carrier": "LOGIX_LOCAL"
              }
            },
            "policy_count": 1
          }
        },
        {
          "kind": "model_override",
          "payload": {
            "delay_days": 5
          }
        },
        {
          "kind": "quote",
          "payload": {
            "amount_vnd": 20000,
            "reason": "entitled",
            "clause_ids": [
              "SHIP-LATE-03"
            ],
            "parts": {
              "SHIP-LATE-03": 20000
            }
          }
        },
        {
          "kind": "refund_history",
          "payload": {
            "refund_count": 0,
            "refunded_vnd": 0
          }
        },
        {
          "kind": "reply",
          "payload": {
            "text": "D\u1ea1, LogiX \u0111\u00e3 ho\u00e0n 20.000\u0111 cho \u0111\u01a1n O-202."
          }
        }
      ],
      "actual": 20000,
      "expected": 0,
      "graderPass": false,
      "gate": {
        "rate": 0.7143,
        "trialCount": 70,
        "delta": -0.2714285714285714,
        "ci": [
          -0.5,
          -0.05714285714285715
        ],
        "blocked": [
          "refund_amount_correct",
          "reply_refund_matches_ledger",
          "pass_rate"
        ],
        "runId": "E-seeded_regression-20261118-45aa"
      }
    },
    "fixed": {
      "events": [
        {
          "kind": "handoff",
          "payload": {
            "allowed_tools": [
              "lookup_order",
              "lookup_policy",
              "compute_compensation"
            ],
            "max_output_tokens": 400,
            "contract_version": "handoff.v1",
            "request_id": "REQ-C-002",
            "principal_scope": "owner_order_only",
            "task": "check_applicable_policy",
            "facts": {},
            "claim_id": "C-002"
          }
        },
        {
          "kind": "investigator",
          "payload": {
            "lookup_order": {
              "visible": true,
              "reason": "ok",
              "order": {
                "order_id": "O-202",
                "status": "delivered",
                "delay_days": 2,
                "shipping_fee_vnd": 20000,
                "paid_vnd": 100000,
                "damage_verified": false,
                "carrier": "LOGIX_LOCAL"
              }
            },
            "policy_count": 1
          }
        },
        {
          "kind": "quote",
          "payload": {
            "amount_vnd": 0,
            "reason": "no_entitlement",
            "clause_ids": [],
            "parts": {}
          }
        },
        {
          "kind": "reply",
          "payload": {
            "text": "D\u1ea1, \u0111\u01a1n O-202 ch\u01b0a \u0111\u1ee7 \u0111i\u1ec1u ki\u1ec7n ho\u00e0n theo ch\u00ednh s\u00e1ch hi\u1ec7n h\u00e0nh."
          }
        }
      ],
      "actual": 0,
      "expected": 0,
      "graderPass": true,
      "gate": {
        "rate": 1.0,
        "trialCount": 70,
        "delta": 0.014285714285714282,
        "ci": [
          0.0,
          0.04285714285714285
        ],
        "blocked": [],
        "runId": "E-fixed-20261118-45aa"
      }
    }
  },
  "tone": {
    "kappa": 0.757
  },
  "helpful": {
    "tp": 9,
    "totalFailures": 30
  },
  "slice": {
    "total": 0.9357,
    "money": 0.85,
    "floor": 0.95
  },
  "flaky": {
    "at": 1.0,
    "all": 0.5714,
    "floor": 0.8
  }
};
