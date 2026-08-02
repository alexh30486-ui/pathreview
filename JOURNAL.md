## Week 7 — Issue selection

**Issue link:** https://github.com/jamjamgobambam/pathreview/issues/153  
**Issue title:** Faithfulness checker crashes when a context chunk has `text: None`  
**Tier:** [x] Tier 1 [ ] Tier 2 [ ] Tier 3  

**Problem summary:**  
I chose this issue to strengthen the reliability of PathReview’s RAG evaluation pipeline without changing scoring behavior or any user-facing features.  

The `FaithfulnessChecker` (`rag/evaluator/faithfulness_checker.py`) determines whether model-generated claims are supported by retrieved context. When an upstream retrieval step returns a chunk shaped like `{"text": None}`, the checker’s string-aggregation logic fails: `dict.get("text", "")` still returns `None` (because the key exists), so `" ".join(...)` raises `TypeError`.  

The fix adds a single defensive coercion at the evaluator boundary so every context value is normalized to a string before concatenation. This keeps the pipeline robust against malformed external data while leaving existing scoring logic untouched.
## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/alexh30486-ui/pathreview/commit/5735928  

**Reproduction summary:**  
Reproduced locally with:

```python
FaithfulnessChecker().check("Knows Python.", [{"text": None}])

 This raised the issue:
TypeError: sequence item 0: expected str instance, NoneType found

Confirmed that Python’s .get("text", "") still returns None when the key "text" is present and holds an explicit None value. Because the default empty string is never used, the subsequent " ".join(...) call receives a NoneType and crashes. The same call works correctly when the chunk contains a normal string or when the "text" key is missing entirely, isolating the failure to the explicit-None case.

PLAN.md link: https://github.com/alexh30486-ui/pathreview/blob/fix/153-faithfulness-none-text/PLAN.md
Walkthrough video (recommended): N/A
Blockers or open questions: None.


**Chunk 3 of 4 — Week 9 Check-in 1**

```markdown
## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**  
Completed the following sub-tasks from PLAN.md:
- Isolated and reproduced the exact `TypeError` in `rag/evaluator/faithfulness_checker.py`.
- Documented root cause, module mapping, and edge cases in `PLAN.md`.
- Implemented the defensive fix: text extraction now uses `(chunk.get("text") or "")` so `None` values are safely coerced to empty strings before concatenation.

**Next steps:**  
- Add a focused unit test for the `None`-text case in `tests/unit/test_faithfulness_checker.py`.
- Run `make check` and `make test-unit` and confirm the change introduces no new failures.
- Open draft PR #245, request peer/mentor feedback, then mark the PR ready for review.

**Blockers:**  
None.
