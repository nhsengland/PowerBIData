def change_to_negative_percentage(percentage_str):
    '''applies a negative symbol and adds the percentage symbol to any string that is a float given'''
    try:
        float(percentage_str[:-1])
        return f"{float(percentage_str[:-1])*-1}%"
    except:
        return percentage_str

def procedure_measure(procedures,measures):
    '''combines the procedures and measures lists to be able to create the proceduremeasure column'''
    procedures = procedures.values.tolist()
    measures = measures.values.tolist()
    proc_mes = [f"{procedures[i]}-{measures[i]}" for i in range(len(measures))]
    return proc_mes


def add_percentage_symbol(column):
    '''adds the percentage symbol to every value in a dataframe column'''
    column_values = column.values.tolist()
    percentages_added = [str(row)+'%' for row in column_values]
    return percentages_added