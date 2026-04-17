import os
import uuid
import csv

HISTORY_FILE="DATA/student_history.csv"

def generate_enrollment(student_name,course):
    name_part=student_name.strip().lower().replace(" ","")
    name_part=name_part[:4]
    random_part=str(uuid.uuid4())[:4]
    enrollment_id=f"{name_part}-{random_part}"
    password=str(uuid.uuid4())[:4]

    file_exists=os.path.isfile(HISTORY_FILE)
    write_header = (not file_exists) or (os.stat(HISTORY_FILE).st_size == 0)

    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["enrollment_id", "student_name", "password", "course"])
        writer.writerow([enrollment_id, student_name, password, course])

    return enrollment_id, password