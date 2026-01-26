import re
import json

def parse_voter_txt(file_path):
    voters = []
    current = {}

    polling_station = None
    ward = None

    pending_relation = None     # Father / Husband
    pending_key = None          # Name waiting for value

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [l.rstrip() for l in f if l.strip()]

    for line in lines:

        # --------------------------------------------------
        # Polling station & ward
        # --------------------------------------------------
        if line.startswith("Polling Station Location"):
            polling_station = line.replace(
                "Polling Station Location:", ""
            ).strip()
            continue

        if line.startswith("Ward:"):
            ward = line.replace("Ward:", "").strip()
            continue

        # --------------------------------------------------
        # New voter record
        # --------------------------------------------------
        if re.match(r"^\d+\s+A\.C No\.-PS No\.-SLNo\.", line):
            if current:
                voters.append(current)
                current = {}

            m = re.search(r":\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)", line)
            if m:
                current["ac_no"], current["ps_no"], current["sl_no"] = m.groups()

            current["polling_station"] = polling_station
            current["ward"] = ward
            continue

        # --------------------------------------------------
        # NAME (robust)
        # --------------------------------------------------
        if re.match(r"^Name\s*:?", line):
            value = line.replace("Name", "").replace(":", "").strip()
            if value:
                current["name"] = value
            else:
                pending_key = "name"
            continue

        if pending_key == "name":
            current["name"] = line.replace(":", "").strip()
            pending_key = None
            continue

        # --------------------------------------------------
        # RELATION (Father / Husband)
        # --------------------------------------------------
        if line.startswith("Father Name"):
            current["relation_type"] = "Father"
            value = line.replace("Father Name", "").replace(":", "").strip()
            if value:
                current["relation_name"] = value
            else:
                pending_relation = "Father"
            continue

        if line.startswith("Husband"):
            current["relation_type"] = "Husband"
            pending_relation = "Husband"
            continue

        if pending_relation and line.startswith("Name"):
            pending_key = "relation_name"
            continue

        if pending_key == "relation_name":
            current["relation_name"] = line.replace(":", "").strip()
            pending_key = None
            pending_relation = None
            continue

        # --------------------------------------------------
        # AGE & SEX
        # --------------------------------------------------
        if "Age" in line:
            age = re.search(r"Age\s*:\s*(\d+)", line)
            sex = re.search(r"Sex\s*:\s*:?\s*(M|F)", line)
            if age:
                current["age"] = int(age.group(1))
            if sex:
                current["sex"] = sex.group(1)
            continue

        # --------------------------------------------------
        # DOOR NO
        # --------------------------------------------------
        if line.startswith("Door No"):
            m = re.search(r"Door No\.?\s*:?\s*(.+)", line)
            if m:
                current["door_no"] = m.group(1).strip()
            continue

        # --------------------------------------------------
        # EPIC NO (fully tolerant)
        # --------------------------------------------------
        if "EPIC" in line:
            m = re.search(r"EPIC\s*No\.?\s*:?\s*([A-Z0-9]+)", line)
            if m:
                current["epic_no"] = m.group(1)
            continue

    if current:
        voters.append(current)

    return voters


if __name__ == "__main__":
    voters = parse_voter_txt("voters.txt")

    with open("voters.json", "w", encoding="utf-8") as f:
        json.dump(voters, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed {len(voters)} voters safely")
