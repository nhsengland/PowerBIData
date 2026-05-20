import pandas as pd
import shutil
from config import PUB_FILE_NAME, PROVISIONAL
from utils.map import using_map_data, map_previous_year
from utils.keyfacts import retrieve_key_facts, last_year_retrieve_key_facts
from utils.indquest import individual_questions_kr_table,individual_questions_hr_table,individual_questions_hr_table_old,individual_questions_kr_table_old
from utils.googlemaps import google_maps_data
from utils.annualCC import annual_report_ahg_table,success_satisfaction,success_satisfaction_old,complications_table,complications_table_old,annual_report_ahg_table_old

shutil.copy("utils\\PowerBIDataEmpty.xlsx", PUB_FILE_NAME)

old_map_data = map_previous_year()
newest_map = using_map_data()
new_map_data = pd.concat([old_map_data, newest_map])

new_key_facts = retrieve_key_facts()
old_key_facts = last_year_retrieve_key_facts()
all_key_facts = pd.concat([old_key_facts, new_key_facts])

hr_individual_questions = individual_questions_hr_table()
kr_individual_questions = individual_questions_kr_table()
hr_individual_questions_old = individual_questions_hr_table_old()
kr_individual_questions_old = individual_questions_kr_table_old()
all_individual_questions = pd.concat([hr_individual_questions_old,kr_individual_questions_old,hr_individual_questions,kr_individual_questions])

googlemaps = google_maps_data()

with pd.ExcelWriter(
    PUB_FILE_NAME, engine="openpyxl", mode="a", if_sheet_exists="overlay"
) as writer:
    new_map_data.to_excel(
        writer, sheet_name="Map", index=False, header=False, startrow=1
    )
    all_key_facts.to_excel(
        writer, sheet_name="Improvement", index=False, header=False, startrow=1
    )
    all_individual_questions.to_excel(
        writer, sheet_name="IndQuest", index=False, header=False, startrow=1
    )
    googlemaps.to_excel(
        writer, sheet_name="Google maps", index=False, header=False, startrow=1
    )


if not PROVISIONAL:
    annualreportahg = annual_report_ahg_table()
    annualreportahg_old = annual_report_ahg_table_old()
    all_ahg = pd.concat([annualreportahg_old, annualreportahg])

    successsatisf = success_satisfaction()
    successsatisf_old = success_satisfaction_old()
    all_successsatisf = pd.concat([successsatisf_old, successsatisf])

    complications = complications_table()
    complications_old = complications_table_old()
    all_complications = pd.concat([complications_old,complications])
    
    with pd.ExcelWriter(PUB_FILE_NAME, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        all_ahg.to_excel(
            writer, sheet_name="Report_AHG", index=False, header=False, startrow=1
        )
        all_successsatisf.to_excel(
            writer,
            sheet_name="Success_Satisfaction",
            index=False,
            header=False,
            startrow=1,
        )
        all_complications.to_excel(
            writer,
            sheet_name="Readmissions_Complications",
            index=False,
            header=False,
            startrow=1,
        )
# gitlab PAC PF2Xaq_3xZKBJrzDzuxz
