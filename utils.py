import pandas as pd
import io
import re
from datetime import datetime

def parse_period(period_str):
    try:
        period_str = period_str.strip()
        if "-" not in period_str:
            return None

        start_str, end_str = [s.strip() for s in period_str.split("-")]
        
        def to_date(s, is_start):
            try:
                if re.match(r"\d{1,2}/\d{4}$", s):
                    d = datetime.strptime(s, "%m/%Y")
                    return datetime(d.year, d.month, 1) if is_start else datetime(d.year, d.month, 30)
                elif re.match(r"\d{1,2}/\d{1,2}/\d{4}$", s):
                    return datetime.strptime(s, "%d/%m/%Y")
                else:
                    return None
            except:
                return None

        start = to_date(start_str, True)
        end = to_date(end_str, False)
        if start and end and start <= end:
            return (start, end)
        return None
    except:
        return None

def get_unique_periods(periods):
    all_days = set()
    unique_days = set()

    for start, end in periods:
        days = set(pd.date_range(start, end))
        if not days.issubset(all_days):
            unique_days.update(days - all_days)
            all_days.update(days)
    
    return len(unique_days) / 30  # Convert to person-months

def process_excel_file(file):
    df = pd.read_excel(file)
    all_periods = []
    person_months_data = []

    for idx, row in df.iterrows():
        row_periods = []
        person_months_row = {}
        for col in df.columns:
            val = row[col]
            parsed = parse_period(val) if isinstance(val, str) else None
            if parsed:
                row_periods.append(parsed)
                days = (parsed[1] - parsed[0]).days + 1
                person_months_row[f"Ανθρωπομήνες_{col}"] = round(days / 30, 1)
            else:
                person_months_row[f"Ανθρωπομήνες_{col}"] = None

        if row_periods:
            all_periods.extend(row_periods)
            person_months_data.append({**row.to_dict(), **person_months_row})

    if not person_months_data:
        return pd.DataFrame(), 0.0, io.BytesIO()

    new_df = pd.DataFrame(person_months_data)
    total_months = round(get_unique_periods(all_periods), 1)

    total_row = {col: "" for col in new_df.columns}
    for col in new_df.columns[::-1]:
        if col.startswith("Ανθρωπομήνες_"):
            total_row[col] = f"Σύνολο: {total_months:.1f}"
            break
    new_df.loc[len(new_df)] = total_row

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        new_df.to_excel(writer, index=False)
    output.seek(0)

    return new_df, total_months, output
