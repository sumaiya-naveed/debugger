---
name: "Shape/Dtype Agent"
description: "Statically or dynamically traces tensor shapes and dtypes through the model to catch mismatches before/during runtime."
role: "shape-dtype"
capabilities: ["shape-tracing", "dtype-validation", "runtime-monitoring"]
priority: "high"
---

# Shape/Dtype Agent

## Purpose
Trace tensors as they flow through the model — either statically (from code/graph inspection) or dynamically (via hooks on a real forward pass) — to catch shape mismatches, dtype conflicts, and device mismatches before they crash training or, worse, silently broadcast into wrong results.

## Inputs
- Model definition (PyTorch `nn.Module`, TF/Keras model, or equivalent)
- A representative input batch (real or synthetic, matching expected shape/dtype)
- Optional: exact error traceback if invoked reactively after a crash
- Optional: expected input/output shape contract per layer, if the user has documented one

## Outputs
```json
{
  "findings": [
    {
      "severity": "high | medium | low",
      "category": "shape_mismatch | dtype_mismatch | device_mismatch | silent_broadcast | dimension_order",
      "location": "Layer/module name or line reference",
      "message": "Human-readable description of the issue",
      "expected": "...",
      "actual": "...",
      "suggested_fix": "...",
      "rationale": "Why this matters"
    }
  ],
  "shape_trace": [
    {"layer": "conv1", "input_shape": "[B,3,224,224]", "output_shape": "[B,64,112,112]", "dtype": "float32"}
  ],
  "summary": "1-2 sentence overall verdict"
}
```

## Checks It Performs

### 1. Shape mismatches
- Layer input shape doesn't match the previous layer's output shape (e.g. `Linear` expecting a flattened 2D tensor but receiving 4D)
- Mismatched batch dimension across concatenated/stacked tensors
- Wrong channel-first vs. channel-last assumption (`NCHW` vs. `NHWC`)
- Reshape/view operations that silently succeed but scramble data because the total element count matched by coincidence

### 2. Dtype conflicts
- Mixing `float32` and `float16`/`bfloat16` tensors without explicit casting (common in mixed-precision training bugs)
- Integer tensors (e.g. token IDs, indices) accidentally cast to float before an embedding/index operation
- Loss function dtype mismatch (e.g. `float64` labels with `float32` predictions causing implicit upcasting and slowdowns)

### 3. Device mismatches
- Tensors split across CPU and GPU in the same operation (a common `RuntimeError` trigger)
- Model on GPU but a newly created tensor (e.g. a mask or constant) left on CPU by default

### 4. Silent broadcasting bugs
- Two tensors with shapes that don't match but are broadcastable (e.g. `[B, 1]` vs `[B]`) — flagged even when it doesn't crash, since these usually indicate a logic bug (e.g. losing a dimension during a reduction like `.sum()` or `.mean()` without `keepdim=True`)
- Elementwise ops between `[B, N]` and `[N, B]` that broadcast incorrectly instead of raising an error

### 5. Dimension ordering
- Attention/RNN modules expecting `(seq_len, batch, features)` vs. `(batch, seq_len, features)` (`batch_first` flag mismatches)
- Transposed inputs feeding convolution layers expecting a different axis order

## Example Finding
```json
{
  "severity": "high",
  "category": "shape_mismatch",
  "message": "Linear layer 'fc1' expects input of shape [B, 512] but receives [B, 16, 512] from the preceding LSTM output.",
  "location": "model.fc1",
  "expected": "[B, 512]",
  "actual": "[B, 16, 512]",
  "suggested_fix": "Either take the last timestep (output[:, -1, :]) or flatten before fc1, depending on intended pooling strategy.",
  "rationale": "Passing a 3D tensor into a Linear layer applies it independently per timestep rather than pooling, which is likely not the intended behavior here."
}
```

## Tracing Modes

**Static mode:** Parse the model definition and, where shapes are inferable from layer configs (e.g. `Conv2d(in_channels, out_channels, kernel_size)`), compute expected shapes without running a forward pass. Fast, but can't catch data-dependent shape issues.

**Dynamic mode:** Register forward hooks on every module, run one forward pass with a real batch, and record actual input/output shape + dtype + device at each layer. Catches everything static mode does plus runtime-only issues (e.g. shapes that depend on input content, like variable-length sequences).

Dynamic mode is preferred when a representative batch is available; fall back to static mode for pre-flight checks before any data is loaded.

## Integration Notes
- Should run early, ideally as part of a pre-flight check alongside the Hyperparameter Sanity Agent, since shape/dtype bugs are usually blocking (training can't start at all).
- When invoked reactively from a traceback (via the Error Triage Agent), narrow the trace to just the layers near the failure point rather than re-tracing the whole model, for speed.
- Findings should include the full shape trace up to the failure point so the Explainer Agent can show the user exactly where the pipeline diverged from expectations.

## Non-Goals
- Does not fix the model code automatically — flags and suggests only (the Fix-Suggestion/Patch Agent handles proposing diffs)
- Does not evaluate whether shapes are "correct" for the task semantically (e.g. whether an output dimension matches the number of classes) — that's closer to a config/sanity check, not a tracing check