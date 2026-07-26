"""Check if generated feedback is supported by retrieved context."""

import re

import structlog

logger = structlog.get_logger()


class FaithfulnessChecker:
    """Verify that feedback claims are supported by context."""

    def check(self, feedback: str, context_chunks: list[dict]) -> float:
        """Check faithfulness of feedback to context.

        Args:
            feedback: Generated feedback text
            context_chunks: Retrieved context chunks

        Returns:
            Faithfulness score 0.0-1.0 (ratio of supported claims)
        """
        if not feedback or not context_chunks:
            logger.info(
                "faithfulness_empty_input",
                has_feedback=bool(feedback),
                has_chunks=bool(context_chunks),
            )
            return 0.0

        # Extract key claims from feedback (sentences)
        claims = self._extract_claims(feedback)
        if not claims:
            logger.info("faithfulness_no_claims_extracted")
            return 0.5  # Default to neutral if no extractable claims

        # Concatenate context text
        context_text = " ".join([(chunk.get("text") or "") for chunk in context_chunks])

        # Check each claim for support using proportional overlap
        supported = 0.0
        for claim in claims:
            supported += self._calculate_support_ratio(claim, context_text)

        score = supported / len(claims) if claims else 0.0

        logger.info(
            "faithfulness_checked", claims_count=len(claims), supported_count=supported, score=score
        )

        return score

    @staticmethod
    def _extract_claims(text: str) -> list[str]:
        """Extract key claims from feedback text.

        Args:
            text: Feedback text

        Returns:
            List of claims (sentences)
        """
        # Split by sentence (simple regex)
        sentences = re.split(r"[.!?]+", text)
        claims = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return claims[:10]  # Limit to 10 claims for scoring

    @staticmethod
    def _calculate_support_ratio(claim: str, context: str) -> float:
        """Calculate the proportion of meaningful claim tokens supported by context."""
        claim_tokens = set(claim.lower().split())
        context_tokens = set(context.lower().split())

        stop_words = {
            "a",
            "an",
            "the",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "and",
            "or",
            "but",
            "in",
            "of",
            "to",
            "for",
            "that",
            "developer",
        }
        meaningful_claim_tokens = claim_tokens - stop_words
        meaningful_context_tokens = context_tokens - stop_words
        if not meaningful_claim_tokens or not meaningful_context_tokens:
            return 0.0

        meaningful_overlap = meaningful_claim_tokens & meaningful_context_tokens
        if len(meaningful_overlap) >= 2:
            return 1.0
        if len(meaningful_overlap) == 1:
            return 0.75
        return 0.0

    @staticmethod
    def _is_supported(claim: str, context: str) -> bool:
        """Check if a claim is supported by context."""
        return FaithfulnessChecker._calculate_support_ratio(claim, context) > 0.0
