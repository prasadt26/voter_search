import re
import json

def parse_voter_txt(file_path):
    voters = []
    current = {}

    polling_station = None
    ward = None

    pending_relation = None
    pending_key = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [l.rstrip() for l in f if l.strip()]

    for line in lines:

        # -------------------------------
        # Polling station & ward
        # -------------------------------
        if line.startswith("Polling Station Location"):
            polling_station = line.replace(
                "Polling Station Location:", ""
            ).strip()
            continue

        if line.startswith("Ward:"):
            ward = line.replace("Ward:", "").strip()
            continue

        # -------------------------------
        # NEW VOTER RECORD (FIXED)
        # -------------------------------
        m = re.match(
            r"^(\d+)\s+A\.C\s+No\.-PS\s+No\.-SLNo\.\s*:\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)",
            line
        )
        if m:
            if current:
                voters.append(current)

            current = {
                "record_serial": int(m.group(1)),
                "ac_no": int(m.group(2)),
                "ps_no": int(m.group(3)),
                "sl_no": int(m.group(4)),
                "polling_station": polling_station,
                "ward": ward
            }
            pending_relation = None
            pending_key = None
            continue

        # -------------------------------
        # NAME (multi-line safe)
        # -------------------------------
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

        # -------------------------------
        # RELATION
        # -------------------------------
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

        # -------------------------------
        # AGE / SEX
        # -------------------------------
        if "Age" in line:
            age = re.search(r"Age\s*:\s*(\d+)", line)
            sex = re.search(r"Sex\s*:\s*:?\s*(M|F)", line)
            if age:
                current["age"] = int(age.group(1))
            if sex:
                current["sex"] = sex.group(1)
            continue

        # -------------------------------
        # DOOR NO
        # -------------------------------
        if line.startswith("Door No"):
            m = re.search(r"Door\s+No\.?\s*:?\s*(.+)", line)
            if m:
                current["door_no"] = m.group(1).strip()
            continue

        # -------------------------------
        # EPIC NO
        # -------------------------------
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

    print(f"✅ Parsed {len(voters)} voters with correct serial numbers")
