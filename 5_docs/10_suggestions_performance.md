
# Performance Tuning

- Optimize Pillow operations; pre-load fonts; reuse buffers if needed.
- Concurrency: tune `MAX_CONCURRENCY` per CPU/GPU.
- Batch requests to reduce overhead; aggregate notify updates.
- S3 uploads: increase part size for large artifacts; parallelize if needed.
