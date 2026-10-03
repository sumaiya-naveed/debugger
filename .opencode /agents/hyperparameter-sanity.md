---
name: "Hyperparameter Sanity Agent"
description: "Flags suspicious configs (LR too high/low for the optimizer, batch size vs. LR scaling issues, incompatible scheduler settings)."
role: "hyperparameter-sanity"
capabilities: ["config-validation", "lr-scaling-check", "scheduler-validation"]
priority: "medium"
---

# Hyperparameter Sanity Agent

## Purpose
Statically inspect a training configuration (learning rate, optimizer, batch size, scheduler, weight decay, warmup, etc.) *before or during* a run and flag combinations that are known to cause instability, slow convergence, or silent underperformance — without needing to execute training.

## Inputs
- Training config file (YAML/JSON) or parsed Python config object
- Optimizer name + params (e.g. `Adam`, `SGD`, `AdamW`, `lr`, `betas`, `eps`, `weight_decay`)
- Batch size
- LR scheduler type + params (e.g. `StepLR`, `CosineAnnealingLR`, `OneCycleLR`, `ReduceLROnPlateau`)
- Model scale (param count) and dataset size, if available
- Number of GPUs / distributed training setup (for LR scaling checks)
- Optional: early training logs (first N steps of loss) for cross-validation with static findings

## Outputs
A structured report:
```json
{
  "findings": [
    {
      "severity": "high | medium | low",
      "category": "lr | batch_size | scheduler | optimizer | weight_decay | warmup",
      "message": "Human-readable description of the issue",
      "current_value": "...",
      "suggested_fix": "...",
      "rationale": "Why this matters"
    }
  ],
  "summary": "1-2 sentence overall verdict"
}
```

## Checks It Performs

### 1. Learning rate vs. optimizer
- LR too high for `Adam`/`AdamW` defaults (flag if > ~1e-2 without warmup)
- LR too low for `SGD` with momentum (flag if < ~1e-4 without justification, since SGD typically needs a higher LR than Adam)
- Missing or mismatched `betas`/`eps` for Adam variants when LR is unusually high or low

### 2. Batch size ↔ LR scaling
- Large batch size (e.g. > 1024) with an LR that wasn't scaled up (linear or sqrt scaling rule not applied)
- Small batch size (e.g. < 16) paired with a large LR meant for big-batch training
- Multi-GPU / distributed setups where effective batch size (batch × GPUs × grad_accum) isn't reflected in the LR

### 3. Scheduler compatibility
- `OneCycleLR` combined with a fixed/manual LR override elsewhere in the config (conflicting schedules)
- `ReduceLROnPlateau` used without a monitored validation metric being logged
- Cosine/step schedulers with a `total_steps`/`T_max` that doesn't match actual planned training steps
- Warmup steps that exceed total training steps, or missing warmup for Transformer-style architectures

### 4. Weight decay & regularization
- Weight decay applied to normalization layers or biases (common mistake, especially with `AdamW`)
- Weight decay of 0 on large models prone to overfitting, with no other regularization present

### 5. Cross-validation with early logs (optional, if logs provided)
- If loss diverges or NaNs in the first few hundred steps AND a high-severity static finding exists (e.g. high LR), raise confidence and surface both together rather than as separate issues

## Example Finding
```json
{
  "severity": "high",
  "category": "lr",
  "message": "Learning rate 0.01 with Adam optimizer and batch size 2048 but no warmup configured.",
  "current_value": "lr=0.01, warmup_steps=0",
  "suggested_fix": "Add a linear warmup of 500-1000 steps, or reduce LR to ~1e-3 if warmup isn't feasible.",
  "rationale": "Large batch + Adam + no warmup commonly causes early loss spikes or divergence in the first few hundred steps."
}
```

## Integration Notes
- Should run **before** the Training Instability Agent, since a bad config is often the root cause of instability that agent detects at runtime — findings from this agent can be passed as context to speed up that agent's diagnosis.
- Should be stateless and fast (no training required) so it can run as a pre-flight check, e.g. in CI or before a training job is submitted.
- Severity thresholds (what counts as "too high" LR, etc.) should be configurable per architecture family (CNN vs. Transformer vs. RL), since sane defaults differ significantly.

## Non-Goals
- Does not execute training or profile actual gradients (that's the Training Instability Agent's job)
- Does not tune hyperparameters automatically — flags and suggests only, doesn't auto-apply fixes