
# Queue Drain Procedure

1. Stop the orchestrator background loop (`ORCH_AUTOSTART=0`).
2. Allow GPU workers to finish in-flight jobs.
3. Snapshot queue depth and job states (export to CSV if desired).
4. If needed, move stale job IDs to a quarantine list and notify users.
5. Resume orchestrator and verify successful completion of remaining jobs.
