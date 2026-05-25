"""Codebook allowed values — keep in sync with codebook.md."""

from __future__ import annotations

CODING_COLUMNS = [
    "code_var_a",
    "code_var_b",
    "code_var_c",
    "code_var_d",
    "code_var_e",
    "code_var_f",
    "code_var_g",
    "code_var_r",
]

META_COLUMNS = ["coder_id", "coded_at", "notes"]

ALLOWED: dict[str, set[str] | None] = {
    "code_var_a": {
        "obey",
        "secret_bury",
        "legal_challenge",
        "compromise",
        "undecided",
    },
    "code_var_b": {
        "relative",
        "authorities",
        "deceased",
        "law_rule",
        "enforcers",
        "unrest_risk",
        "society",
        "distributed",
    },
    "code_var_c": {
        "legal_obedience",
        "human_dignity",
        "family_duty",
        "public_order",
        "sacred_dead_duty",
        "procedure_proportionality",
        "consequentialist_harm",
        "virtue_conscience",
    },
    "code_var_d": {
        "individualized",
        "institutional",
        "deagentive",
        "circumstantial",
        "relational_affected",
    },
    "code_var_e": {
        "terrorist_enemy",
        "human",
        "family_member",
        "criminal_with_dignity",
        "political_symbol",
    },
    "code_var_f": {
        "decisive",
        "manageable",
        "speculative",
        "state_produced",
        "secondary",
    },
    # comma-separated tags allowed
    "code_var_g": {
        "judicial_review",
        "appeal_administrative",
        "independent_risk_assessment",
        "supervised_private_burial",
        "time_place_restrictions",
        "explanation_compensation_family",
        "none",
    },
    "code_var_r": {
        "mirrors_register",
        "mirrors_evidential",
        "mirrors_aspect",
        "flattens_neutral",
    },
}

REQUIRED_PHASE1 = ["code_var_a", "code_var_b"]
RECOMMENDED_PHASE1 = ["code_var_c", "code_var_d"]
REQUIRED_PHASE1_JA = ["code_var_r"]
