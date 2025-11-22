import time
import pandas as pd
from csv import reader
from pywebio.input import *
from pywebio.output import *
from email_sender import send_allotment_email

# Images for UI
header_img = open('images/header.jpg', 'rb').read()
success_image = open("images/success.png", 'rb').read()

# Allotment lists
comp_allotment = []
IT_allotment = []
mech_allotment = []
elec_allotment = []
all_allotments = [comp_allotment, IT_allotment, mech_allotment, elec_allotment]
no_allotment = []


class Allotment_mechanism:

    def __init__(self):
        self.allotment_done = False
        self.vacancies = {0: 120, 1: 60, 2: 60, 3: 120}

    # ------------------------------------------------------------
    # RUN ALLOTMENT
    # ------------------------------------------------------------
    def run_allotment(self):
        global comp_allotment, IT_allotment, mech_allotment, elec_allotment, no_allotment

        if self.allotment_done:
            with use_scope('ROOT'):
                put_image(header_img, width='100%', height='50px')
                put_html("<br><br>")

            with use_scope("main", clear=True):
                put_success("Allotment process already done!")

                data = input_group("Reset?", [
                    actions("", [
                        {'label': 'Back', 'value': 1},
                        {'label': 'Reset Allotment', 'value': 2}
                    ], name='action')
                ])

                if data["action"] == 2:
                    self.reset_allotment()

            clear('ROOT')
            return

        # UI
        with use_scope('ROOT'):
            put_image(header_img, width='100%', height='50px')
            put_html("<br><br>")
        with use_scope("main", clear=True):
            put_text("Running allotment... Please wait")

        df = pd.read_csv("datasheet.csv")

        # Ensure numeric prefs/marks
        for col in ["PREF1", "PREF2", "PREF3", "MARKS"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Students with complete applications
        valid_df = df[(df["PREF1"] >= 0) & (df["PREF2"] >= 0) & (df["PREF3"] >= 0)]
        valid_df = valid_df.sort_values("MARKS", ascending=False)

        # Clear old lists
        comp_allotment.clear()
        IT_allotment.clear()
        mech_allotment.clear()
        elec_allotment.clear()
        no_allotment.clear()

        # Preference allocation
        for _, row in valid_df.iterrows():
            name = row["NAME"].strip()
            surname = row["SURNAME"].strip()

            prefs = [int(row["PREF1"]), int(row["PREF2"]), int(row["PREF3"])]
            allocated = False

            for p in prefs:
                if self.vacancies[p] > 0:
                    self.vacancies[p] -= 1
                    all_allotments[p].append((name, surname))
                    allocated = True
                    break

            if not allocated:
                no_allotment.append((name, surname))

        # Update CSV + send emails
        self.update_allotments()

        self.allotment_done = True

        # UI
        with use_scope("main"):
            put_processbar("bar")
            for i in range(10):
                set_processbar("bar", (i+1)/10)
                time.sleep(0.1)

            put_image(success_image, width="20%", height="20%")
            put_success("Allotment completed successfully")

            input_group("Done", [
                actions("", [{'label': 'Back', 'value': 1}], name='action')
            ])

        clear('ROOT')

    # ------------------------------------------------------------
    # RESET ALLOTMENT
    # ------------------------------------------------------------
    def reset_allotment(self):
        global comp_allotment, IT_allotment, mech_allotment, elec_allotment, no_allotment

        self.allotment_done = False
        self.vacancies = {0: 120, 1: 60, 2: 60, 3: 120}

        comp_allotment.clear()
        IT_allotment.clear()
        mech_allotment.clear()
        elec_allotment.clear()
        no_allotment.clear()

        df = pd.read_csv("datasheet.csv")
        df["ALLOTMENT"] = "-"
        df.to_csv("datasheet.csv", index=False)

        put_success("Allotment has been reset.")

    # ------------------------------------------------------------
    # GET ROW NUMBER BY NAME + SURNAME (case-insensitive)
    # ------------------------------------------------------------
    def get_row(self, person):
        target_name = person[0].lower().strip()
        target_surname = person[1].lower().strip()

        with open("datasheet.csv", "r") as f:
            csv_reader = reader(f)
            for idx, row in enumerate(csv_reader):
                if len(row) < 2:
                    continue
                if row[0].lower().strip() == target_name and row[1].lower().strip() == target_surname:
                    return idx + 1  # 1-based index

        return -1

    # ------------------------------------------------------------
    # UPDATE ALLOTMENTS + SEND EMAILS
    # ------------------------------------------------------------
    def update_allotments(self):
        global comp_allotment, IT_allotment, mech_allotment, elec_allotment, no_allotment

        with open("datasheet.csv", "r") as f:
            lines = f.read().splitlines()

        def update_branch(allot_list, branch):
            for person in allot_list:
                row_no = self.get_row(person)
                if row_no == -1:
                    continue

                fields = lines[row_no-1].split(",")
                fields[7] = branch
                lines[row_no-1] = ",".join(fields)

                # Send email
                send_allotment_email(
                    to_email=fields[2],
                    student_name=fields[0],
                    branch=branch
                )

        # Branch updates
        update_branch(comp_allotment, "Computer")
        update_branch(IT_allotment, "IT")
        update_branch(mech_allotment, "Mechanical")
        update_branch(elec_allotment, "Electronics")

        # ------------------------
        # EMAIL FOR NOT ALLOTTED
        # ------------------------
        for person in no_allotment:
            row_no = self.get_row(person)
            if row_no == -1:
                continue

            fields = lines[row_no-1].split(",")

            send_allotment_email(
                to_email=fields[2],
                student_name=fields[0],
                branch="No Seat Allotted"
            )

        # Save CSV
        with open("datasheet.csv", "w") as f:
            for line in lines:
                f.write(line + "\n")

    # ------------------------------------------------------------
    # GET CUTOFF MARKS
    # ------------------------------------------------------------
    def get_cutoffs(self, branch):
        group_map = {
            "comp": comp_allotment,
            "it": IT_allotment,
            "mech": mech_allotment,
            "entc": elec_allotment
        }

        lst = group_map.get(branch)
        if not lst:
            return 0

        last_person = lst[-1]

        with open("datasheet.csv", "r") as f:
            csv_reader = reader(f)
            for row in csv_reader:
                if row[0].lower() == last_person[0].lower() and row[1].lower() == last_person[1].lower():
                    return row[3]

        return 0
