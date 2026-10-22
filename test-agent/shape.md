Here are the tracing rules from the repo's Shape/Dtype agent spec (`.opencode/agents/shape-dtype.md:53-98`):

**Core checks**
1. **Shape mismatches** — each layer's input must match the previous layer's output; flag batch-dim inconsistencies, NCHW vs. NHWC channel-order errors, Linear layers receiving non-flattened 3D/4D tensors, and reshape ops whose element counts merely coincided.
2. **Dtype conflicts** — no implicit mixing of `float32`/`float16`/`bfloat16` without explicit casts; integer token IDs shouldn't be cast to float before embedding/index ops; loss labels dtype vs. prediction dtype (e.g., `float64` labels vs. `float32` preds).
3. **Device mismatches** — CPU/GPU tensors split across one op; model on GPU with CPU-resident masks/constants.
4. **Silent broadcasting bugs** — flag broadcastable-but-unequal shapes (e.g., `[B,1]` vs `[B]`) or `[B,N]` vs `[N,B]` even when no crash occurs (lost dims from `.sum()`/`.mean()` without `keepdim=True`).
5. **Dimension ordering** — attention/RNN modules expecting `(seq_len, batch, features)` vs. `(batch, seq_len, features)` (`batch_first` flag mismatches).

**Tracing modes**
- **Static:** infer shapes from layer configs (e.g., `Conv2d(in, out, kernel)`) without a forward pass — fast but can't catch data-dependent shapes.
- **Dynamic:** register forward hooks on each module, run one real forward pass, record actual input/output shape + dtype + device per layer — preferred when a representative batch exists; falls back to static for pre-flight checks.

The full finding schema (severity, category, location, expected/actual shapes, rationale) and shape trace output are defined at `.opencode/agents/shape-dtype.md:31-50`.
