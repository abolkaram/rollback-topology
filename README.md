# Rollback Topology

## Incident notebook · sheet 01

Systems are graphs, but rollback instructions are often written as prose. That mismatch is dangerous: undoing a database before its dependent API can turn a recoverable incident into a second outage.

Rollback Topology stores the graph as indexed nodes and edges (`dependency → dependent`). During an incident, a named responder anchors two independent artifacts—the incident report and proposed runbook. Validators extract the impacted nodes and proposed order. The contract then performs the safety calculation itself: every dependent must roll back before its dependency.

## Decision marks

| Mark | Meaning |
|---|---|
| REGISTERED | topology frozen, no incident plan |
| PLANNED | exact impacted-node permutation is dependency-safe |
| BLOCKED | one or more stored edges are reversed by the plan |
| RESTORED | execution evidence covers every impacted node successfully |
| PARTIAL | execution evidence names at least one failed node |
| EXPIRED | a safe plan missed its execution window |

## Why the result is hard to forge

Consensus recomputes source digests and the complete impacted/order arrays. The contract derives `unsafe_edges` deterministically from the frozen graph. Execution then requires an exclusive completed/failed partition of every impacted index, from a third origin.

## Pager drill

`genvm-lint contracts/contract.py` checks the contract. `python -m pytest -q` runs five direct drills, including dependency reversal and a leader result with an omitted node. The numbered evidence files mirror the live incident sequence.
