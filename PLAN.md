# Plan for Issue #153 — Faithfulness checker crashes when a context chunk has text: None

## Problem
The faithfulness evaluation path crashes when a context chunk is provided as a dictionary with a `text` value of `None`. The failure occurs before scoring begins because the code joins context strings using a list comprehension that passes `None` into `" ".join(...)`.

## Goal
Fix the crash in a targeted way while preserving the existing scoring behavior for normal context chunks. The change should make the evaluator resilient to malformed input without altering the intended faithfulness logic for valid data.

## Approach
1. Reproduce the issue locally and confirm the point of failure.
2. Adjust the context normalization step so that missing or invalid text values are treated as empty strings.
3. Add or preserve regression coverage for the `None` case.
4. Run the relevant unit tests to confirm the fix and ensure no regressions were introduced.

## Why this approach
The evaluator is the narrow boundary where retrieved context becomes input for scoring. Handling invalid values there is the smallest change that protects all callers and keeps the rest of the faithfulness logic unchanged.
