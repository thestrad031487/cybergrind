import json
import urllib.request
import os

SOURCES = {
    "enterprise": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
    "ics": "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "data")

def fetch_and_parse(name, url):
    print(f"Fetching {name} ATT&CK bundle...")
    with urllib.request.urlopen(url) as r:
        bundle = json.loads(r.read())

    objects = bundle.get("objects", [])

    tactics = {}
    techniques = []
    relationships = []

    for obj in objects:
        obj_type = obj.get("type")

        if obj_type == "x-mitre-tactic":
            shortname = obj.get("x_mitre_shortname")
            tactics[shortname] = {
                "id": shortname,
                "name": obj.get("name"),
                "description": obj.get("description", "")[:300],
            }

        elif obj_type == "attack-pattern":
            if obj.get("x_mitre_deprecated") or obj.get("revoked"):
                continue
            ext_refs = obj.get("external_references", [])
            attck_id = next(
                (r["external_id"] for r in ext_refs if r.get("source_name") == "mitre-attack"),
                None
            )
            if not attck_id:
                continue
            kill_chain = obj.get("kill_chain_phases", [])
            tactic_refs = [p["phase_name"] for p in kill_chain if p.get("kill_chain_name") == "mitre-attack"]
            techniques.append({
                "id": attck_id,
                "stix_id": obj.get("id"),
                "name": obj.get("name"),
                "description": obj.get("description", "")[:500],
                "tactics": tactic_refs,
                "is_subtechnique": obj.get("x_mitre_is_subtechnique", False),
                "platforms": obj.get("x_mitre_platforms", []),
                "detection": obj.get("x_mitre_detection", "")[:300],
                "url": next(
                    (r["url"] for r in ext_refs if r.get("source_name") == "mitre-attack"),
                    ""
                ),
            })

    tactic_order = [t["name"] for t in sorted(
        tactics.values(),
        key=lambda x: x["name"]
    )]

    output = {
        "tactics": tactics,
        "techniques": techniques,
        "tactic_count": len(tactics),
        "technique_count": len(techniques),
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"attck-{name}.json")
    with open(out_path, "w") as f:
        json.dump(output, f)
    print(f"Wrote {len(techniques)} techniques across {len(tactics)} tactics to {out_path}")

if __name__ == "__main__":
    for name, url in SOURCES.items():
        fetch_and_parse(name, url)