"""Build data/phase1_manual_codes.csv from agent coding passes."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "phase1_manual_codes.csv"

# EN (18) + CS (18) + JA (18) from codebook agent pass
CSV_BLOBS = """
record_id,code_var_a,code_var_b,code_var_c,code_var_d,code_var_e,code_var_f,code_var_g,code_var_r,coder_id,coded_at
0267ccbc-6cb2-4072-afef-aa1411ca0390,compromise,authorities,procedure_proportionality,relational_affected,family_member,manageable,none,,agent,2026-05-25
05699afb-183c-416d-8d38-05adbc89306a,compromise,authorities,procedure_proportionality,relational_affected,family_member,manageable,none,,agent,2026-05-25
0ba55c79-b964-4a94-a8a8-8766bbc1d4db,undecided,authorities,consequentialist_harm,relational_affected,criminal_with_dignity,manageable,"supervised_private_burial,time_place_restrictions",,agent,2026-05-25
0ea464d8-fd8d-4282-8267-729c4e90439b,obey,authorities,legal_obedience,individualized,criminal_with_dignity,decisive,none,,agent,2026-05-25
0ef41bd7-7612-4240-973d-79245b720b21,undecided,authorities,virtue_conscience,individualized,human,speculative,none,,agent,2026-05-25
1f563071-f592-4dfc-8d74-110b177c5736,legal_challenge,authorities,human_dignity,institutional,criminal_with_dignity,state_produced,judicial_review,,agent,2026-05-25
2f861b39-a31c-47c7-89ab-fb4c887e6d3d,compromise,deceased,procedure_proportionality,institutional,criminal_with_dignity,manageable,"judicial_review,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
4c4321ca-ebc4-4d68-9ce4-49bb75378fb2,compromise,deceased,procedure_proportionality,institutional,criminal_with_dignity,manageable,"judicial_review,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
5417ef5b-5572-44e4-b2cb-b11e808ce754,compromise,deceased,human_dignity,institutional,criminal_with_dignity,manageable,"supervised_private_burial,time_place_restrictions",,agent,2026-05-25
72c21c46-d885-45e7-8f92-ac132e642648,secret_bury,deceased,sacred_dead_duty,individualized,criminal_with_dignity,secondary,none,,agent,2026-05-25
743210d1-16d7-4438-95fa-598a78f6d8b1,undecided,authorities,virtue_conscience,individualized,criminal_with_dignity,speculative,none,,agent,2026-05-25
916e91e5-6457-4a0b-b26b-b902027f7e02,compromise,authorities,procedure_proportionality,relational_affected,family_member,manageable,none,,agent,2026-05-25
97d7cf9a-0d16-471f-abc1-bc67f16bae6d,undecided,authorities,virtue_conscience,relational_affected,criminal_with_dignity,manageable,none,,agent,2026-05-25
a8e0f7a9-94fe-4b29-8e10-337b3d696579,compromise,authorities,procedure_proportionality,individualized,criminal_with_dignity,manageable,"supervised_private_burial,time_place_restrictions",,agent,2026-05-25
dba0048e-d26c-4863-8930-025b3792ebf9,undecided,authorities,virtue_conscience,individualized,human,speculative,none,,agent,2026-05-25
e05a16ab-a971-49cb-8e22-13e974d8c9c4,compromise,deceased,procedure_proportionality,institutional,criminal_with_dignity,manageable,"judicial_review,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
e38ae4c8-1de9-4b4c-a239-4419be0810ad,compromise,authorities,procedure_proportionality,relational_affected,criminal_with_dignity,manageable,supervised_private_burial,,agent,2026-05-25
ff588785-e51f-45c2-9f9b-9b601e7812e4,undecided,deceased,virtue_conscience,individualized,human,speculative,none,,agent,2026-05-25
60533d87-4601-4e43-a066-56d404795a0b,legal_challenge,authorities,human_dignity,institutional,family_member,manageable,"appeal_administrative,judicial_review,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
f86903e2-0c6d-49c7-ae92-ec87a4603225,compromise,authorities,human_dignity,institutional,family_member,speculative,"supervised_private_burial,time_place_restrictions",,agent,2026-05-25
fd7e4519-c71e-459c-bc98-13b83b3c60f9,legal_challenge,authorities,human_dignity,institutional,family_member,manageable,"appeal_administrative,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
8c1e1045-90d8-4df0-b2e7-bca3c70f2283,undecided,authorities,human_dignity,institutional,family_member,speculative,"appeal_administrative,judicial_review,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
d05c4b23-91bb-46d1-b1e6-61e5b6c64255,undecided,authorities,human_dignity,institutional,family_member,speculative,"appeal_administrative,judicial_review,supervised_private_burial,time_place_restrictions",,agent,2026-05-25
e6d4c26e-580b-424f-a246-b3448dbd657a,undecided,authorities,human_dignity,institutional,family_member,speculative,"supervised_private_burial,time_place_restrictions",,agent,2026-05-25
c929ae0d-a13c-4f33-8e7a-a962ab17b2a3,undecided,authorities,human_dignity,institutional,human,speculative,none,,agent,2026-05-25
5b40be19-1efa-420f-a0ff-ef08d139f9a0,legal_challenge,authorities,human_dignity,institutional,family_member,manageable,"supervised_private_burial,judicial_review",,agent,2026-05-25
7c9b0e92-4716-4b6c-9445-290458bd1110,compromise,authorities,human_dignity,institutional,family_member,speculative,supervised_private_burial,,agent,2026-05-25
f708d381-f038-430f-a644-d65485368bbf,undecided,authorities,family_duty,institutional,family_member,speculative,judicial_review,,agent,2026-05-25
cdd77444-d12a-4f9a-9b84-14e1a71bbd43,undecided,authorities,family_duty,institutional,family_member,speculative,none,,agent,2026-05-25
3dd0ac37-c0fa-4ddc-af32-1fd682d3ff76,legal_challenge,authorities,human_dignity,institutional,family_member,manageable,supervised_private_burial,,agent,2026-05-25
49b90b60-04fc-4ec8-8a25-918501d07719,compromise,authorities,human_dignity,institutional,family_member,speculative,supervised_private_burial,,agent,2026-05-25
fcabf0ac-0c29-4d84-87bc-241069de5415,compromise,authorities,human_dignity,institutional,family_member,speculative,supervised_private_burial,,agent,2026-05-25
dcc73794-d6e5-40fb-a0ed-e53eb30d57dc,compromise,authorities,human_dignity,institutional,family_member,speculative,supervised_private_burial,,agent,2026-05-25
1ec9eb29-8730-4845-a89a-6b0c48d68537,undecided,authorities,human_dignity,institutional,family_member,speculative,supervised_private_burial,,agent,2026-05-25
b0acba3a-a095-4aab-8d0b-9d40368276a8,undecided,authorities,human_dignity,institutional,family_member,speculative,supervised_private_burial,,agent,2026-05-25
29f8112f-2f76-4215-9344-77e302c20f0c,undecided,authorities,human_dignity,institutional,family_member,speculative,"supervised_private_burial,appeal_administrative",,agent,2026-05-25
00d8c33b-3adb-468e-b989-49b7d6d6b921,legal_challenge,authorities,human_dignity,institutional,human,manageable,"supervised_private_burial,time_place_restrictions",flattens_neutral,agent,2026-05-25
012d6a58-ce1a-4254-aab4-db2f7ec4b58b,compromise,authorities,human_dignity,institutional,human,secondary,"supervised_private_burial,time_place_restrictions",flattens_neutral,agent,2026-05-25
1b1ab8a0-edc6-497f-bf50-28537a20c9cf,undecided,authorities,legal_obedience,individualized,human,speculative,supervised_private_burial,flattens_neutral,agent,2026-05-25
1d3143ca-c2a6-4781-aad7-860b7811af5f,undecided,authorities,human_dignity,institutional,human,speculative,none,flattens_neutral,agent,2026-05-25
30169d33-1e92-4f38-a70b-926149883854,undecided,society,human_dignity,relational_affected,human,speculative,none,flattens_neutral,agent,2026-05-25
3537d72c-5900-4093-96d2-e0d02ec11348,undecided,authorities,human_dignity,institutional,human,speculative,supervised_private_burial,flattens_neutral,agent,2026-05-25
4dd66687-6f1e-419e-b60a-1edf8217d612,undecided,authorities,legal_obedience,individualized,human,speculative,supervised_private_burial,flattens_neutral,agent,2026-05-25
4ddd7ae1-f7a8-4269-b13c-cdb4241bd303,undecided,society,human_dignity,relational_affected,human,speculative,none,flattens_neutral,agent,2026-05-25
55a5064d-ccdd-4e4b-ab5a-d2f9727f7e22,undecided,relative,human_dignity,individualized,family_member,speculative,none,flattens_neutral,agent,2026-05-25
5c01c050-bc50-483e-9e7f-c7abb30236ab,undecided,authorities,human_dignity,institutional,human,speculative,none,flattens_neutral,agent,2026-05-25
67e07a77-74b2-4af8-b600-2a2b231567d3,legal_challenge,authorities,human_dignity,institutional,human,speculative,time_place_restrictions,flattens_neutral,agent,2026-05-25
88fb656c-bc85-489f-aee0-b83c3e4585c2,undecided,authorities,human_dignity,individualized,human,speculative,supervised_private_burial,flattens_neutral,agent,2026-05-25
b493708f-63b6-4b87-9437-3ad4e787c4f3,undecided,authorities,human_dignity,institutional,human,speculative,none,flattens_neutral,agent,2026-05-25
b7587e84-efb4-49eb-9dcd-6c4bf23da1bf,undecided,authorities,human_dignity,institutional,human,speculative,none,flattens_neutral,agent,2026-05-25
c087867a-4909-40a4-b0d8-e59870943fd7,legal_challenge,authorities,human_dignity,institutional,human,speculative,none,flattens_neutral,agent,2026-05-25
cc8216bb-c87b-48d4-9f72-a6035dea6936,undecided,relative,human_dignity,relational_affected,family_member,speculative,none,flattens_neutral,agent,2026-05-25
dcdc6486-35c3-46dc-a380-bc1a77b432bd,undecided,authorities,human_dignity,institutional,human,speculative,none,flattens_neutral,agent,2026-05-25
e28328e0-42c5-4dc0-b9b7-36c1e5d2a7a0,legal_challenge,authorities,human_dignity,institutional,human,manageable,none,flattens_neutral,agent,2026-05-25
"""

FIELDS = [
    "record_id",
    "code_var_a",
    "code_var_b",
    "code_var_c",
    "code_var_d",
    "code_var_e",
    "code_var_f",
    "code_var_g",
    "code_var_r",
    "coder_id",
    "coded_at",
]


def normalize(row: dict[str, str]) -> dict[str, str]:
    for col in ("code_var_c", "code_var_a", "code_var_b", "code_var_d"):
        v = row.get(col, "")
        if "|" in v:
            row[col] = v.split("|")[0].strip()
    return row


def main() -> None:
    import io
    import json

    rows = list(csv.DictReader(io.StringIO(CSV_BLOBS.strip())))
    rows = [normalize(r) for r in rows]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    canon = {
        json.loads(line)["record_id"]
        for line in (
            ROOT / "logs/phase1_20260525T081321Z_8b488b4a/responses.jsonl"
        ).open(encoding="utf-8")
        if line.strip()
    }
    coded = {r["record_id"] for r in rows}
    missing = canon - coded
    extra = coded - canon
    print(f"Wrote {len(rows)} codes to {OUT}")
    if missing:
        print("MISSING", missing)
    if extra:
        print("EXTRA", extra)


if __name__ == "__main__":
    main()
