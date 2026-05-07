# LAB15 - StatefulSets and Persistent Storage

This report covers Lab 15 requirements and references the detailed evidence in [k8s/STATEFULSET.md](k8s/STATEFULSET.md).

## Task 1 - Concepts
- StatefulSets provide stable network identities, stable per-pod storage, and ordered lifecycle management.
- Deployments are preferred for stateless apps; StatefulSets are preferred for stateful workloads (databases, queues, clustered systems).
- Headless services (`clusterIP: None`) create DNS records for each pod in the StatefulSet, enabling stable pod-level DNS.

## Task 2 - Implementation Summary
- Added a StatefulSet template with `volumeClaimTemplates` for per-pod storage.
- Added a headless Service to provide stable DNS entries.
- Kept the external Service for client access.
- Configured StatefulSet update strategy values for rolling updates and partitioning.

## Task 3 - Identity and Storage Tests
See evidence and command outputs in [STATEFULSET](STATEFULSET.md).

## Task 4 - Documentation
The required documentation is in [STATEFULSET](STATEFULSET.md).

## Bonus - Update Strategies
See notes and observations in [STATEFULSET](STATEFULSET.md).
