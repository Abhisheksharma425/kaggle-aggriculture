import zipfile
import csv

zip_filename = 'kaggriculture.zip'

with zipfile.ZipFile(zip_filename) as z:
    csv_name = z.namelist()[0]
    with z.open(csv_name) as f:
        lines = [line.decode('utf-8') for line in f.readlines()]
        reader = csv.DictReader(lines)
        rows = list(reader)

rows.sort(key=lambda x: float(x.get('Score', 0)), reverse=True)

target = "Wei Hsiang Lin111"
found = False

for rank, row in enumerate(rows, 1):
    tname = row.get("TeamName", "")
    score = row.get("Score", "")
    sub_date = row.get("SubmissionDate", "")
    if target.lower() in tname.lower():
        print("=" * 60)
        print("MATCHED COMPETITOR DETAILS:")
        print(f"  Competitor Name : {tname}")
        print(f"  Kaggle Rank     : #{rank} out of {len(rows)} teams")
        print(f"  Public Score    : {score}")
        print(f"  Submission Date : {sub_date}")
        print("=" * 60)
        found = True

if not found:
    print("Searching partial name matches...")
    for rank, row in enumerate(rows, 1):
        tname = row.get("TeamName", "")
        if "hsiang" in tname.lower() or "lin" in tname.lower():
            print(f"  Rank #{rank}: {tname} | Score: {row.get('Score')}")
