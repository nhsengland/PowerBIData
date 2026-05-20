def retrieve_key_facts():
    from utils.connection import connection
    from utils.queries import key_facts
    from config import FYEAR,DATE_TO,TABLE,YEAR_STRING
    from utils.formatting import change_to_negative_percentage,procedure_measure
    import pandas as pd

    cnxn = connection('PROMS_PUBLICATION')
    keyfacts = pd.read_sql(key_facts(FYEAR,DATE_TO,TABLE),cnxn)
    england_mask = keyfacts['Organisation Type'].isin(['England','Provider'])
    england_and_provider_keyfacts = keyfacts[england_mask]

    england_and_provider_keyfacts['% Worsened'] = england_and_provider_keyfacts['% Worsened'].apply(change_to_negative_percentage)
    england_and_provider_keyfacts['% Unchanged'] = england_and_provider_keyfacts['% Unchanged'].apply(change_to_negative_percentage)
    england_and_provider_keyfacts.insert(0,'Financial Year',YEAR_STRING)

    england_and_provider_keyfacts['Procedure Measure']=procedure_measure(england_and_provider_keyfacts['Procedure'],england_and_provider_keyfacts['Measure'])
    ##changing the data type to the correct one
    for column in england_and_provider_keyfacts.columns:
            try:
                england_and_provider_keyfacts[column] = england_and_provider_keyfacts[column].astype('float64')
            except ValueError:
                continue
    return england_and_provider_keyfacts 

def last_year_retrieve_key_facts():
    from utils.connection import connection
    from utils.queries import key_facts
    from config import PREVIOUS_FYEAR,DATE_TO_MIN1,PREVIOUS_TABLE,YEAR_STRING_MIN1
    from utils.formatting import change_to_negative_percentage,procedure_measure
    import pandas as pd

    cnxn = connection('PROMS_PUBLICATION')
    keyfacts = pd.read_sql(key_facts(PREVIOUS_FYEAR,DATE_TO_MIN1,PREVIOUS_TABLE),cnxn)

    england_mask_old = keyfacts['Organisation Type'].isin(['England','Provider'])
    england_and_provider_keyfacts_old = keyfacts[england_mask_old]

    england_and_provider_keyfacts_old['% Worsened'] = england_and_provider_keyfacts_old['% Worsened'].apply(change_to_negative_percentage)
    england_and_provider_keyfacts_old['% Unchanged'] = england_and_provider_keyfacts_old['% Unchanged'].apply(change_to_negative_percentage)
    england_and_provider_keyfacts_old.insert(0,'Financial Year',YEAR_STRING_MIN1)

    england_and_provider_keyfacts_old['Procedure Measure']=procedure_measure(england_and_provider_keyfacts_old['Procedure'],england_and_provider_keyfacts_old['Measure'])
    ##changing the data type to the correct one
    for column in england_and_provider_keyfacts_old.columns:
            try:
                england_and_provider_keyfacts_old[column] = england_and_provider_keyfacts_old[column].astype('float64')
            except ValueError:
                continue
    return england_and_provider_keyfacts_old 
