
# FAQ

**Why Redis?** For simplicity and low ops overhead. Kafka is great when you
need durable streams and consumer groups; we don't for this scope.

**How do I add a new model?** Create a manifest JSON in Model Registry and
update the SPA to surface it; orchestrator/worker contract stays the same.

**Can workers run real models?** Yes — replace `engine.py` with your
inference path (PyTorch/ONNX/TensorRT). Keep the `/generate` contract.
