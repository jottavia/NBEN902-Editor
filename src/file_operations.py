import pandas as pd

def parse_fixed_width_file(file_path):
    colspecs = [(0, 10), (10, 60), (60, 69), (69, 75), (75, 85), (85, 95), (95, 103)]
    column_names = ["Agency Code", "Name", "Employee ID", "Deduction Code", "Effective Date", "Deduction End Date", "Deduction Amount"]
    df = pd.read_fwf(file_path, colspecs=colspecs, header=None, names=column_names, converters={'Agency Code': str})
    return df

def save_data(df, file_path):
    col_widths = [10, 50, 9, 6, 10, 10, 8]
    with open(file_path, "w") as file:
        for _, row in df.iterrows():
            row_str = ""
            for idx, value in enumerate(row):
                if idx == 4 or idx == 5:  # Effective Date and Deduction End Date columns
                    if value == "":
                        value = " " * col_widths[idx]
                if idx == 6:  # Deduction Amount field
                    formatted_value = str(value).rjust(col_widths[idx], '0')
                else:
                    formatted_value = str(value).ljust(col_widths[idx], ' ')
                row_str += formatted_value[:col_widths[idx]]
            file.write(row_str + "\n")
