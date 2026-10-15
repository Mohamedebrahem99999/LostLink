import pandas as pd
from item_repository import ItemRepository


def load_items():
    items = ItemRepository.get_all()

    if not isinstance(items, dict):
        return []

    records = []

    for item_id, item in items.items():
        if isinstance(item, dict):
            record = item.copy()
            record["item_id"] = str(item_id)

            if "status" not in record:
                if record.get("is_open") is True:
                    record["status"] = "open"
                elif record.get("is_open") is False:
                    record["status"] = "closed"
                else:
                    record["status"] = "unknown"

            records.append(record)

    return records


def create_dataframe(items):
    df = pd.DataFrame(items)
    return df

def clean_data(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"],errors = "coerce")

    for column in [
        "category",
        "color",
        "location",
        "status",
        "report_type",
        "name", 
        "description"
        ]:
       if column in df.columns:
           df[column] = df[column].astype("string").str.strip().str.lower()

    return df

def get_data_quality_report(df):
    report = {
        "missing_values": df.isnull().sum().to_dict(), 
        "duplicated_ids":int(df["item_id"].duplicated().sum()),
        "invalid_dates": int(df["date"].isna().sum())
    }
    return report


def get_category_stats(df):
    return df["category"].value_counts()

def get_location_stats(df):
    return df["location"].value_counts()

def get_status_stats(df):
    return df["status"].value_counts()

def get_total_reports(df):
    return len(df) 

def get_match_rate(df):
    if df.empty:
        return 0.0
        
    matched = (df["status"].astype(str).str.strip().str.lower() == "matched").sum()
    return (matched / len(df)) * 100

def get_closure_rate(df):
    if df.empty:
        return 0.0

    closed = (
        df["status"].astype(str).str.strip().str.lower() == "closed"
    ).sum()

    return (closed / len(df)) * 100

def get_time_stats(df):
    return (df.dropna(subset = ["date"]).groupby(df["date"].dt.to_period("M")).size())

def get_chart_data(df):
    category_data = df["category"].value_counts()
    status_data = df["status"].value_counts()
    time_data = get_time_stats(df)

    return category_data, status_data, time_data

def get_insights(df):
    if df.empty:
        return ["No data available for analysis."]

    insights = []

    if "category" in df.columns:
        categories = df["category"].dropna().value_counts()
        if not categories.empty:
            insights.append(
                f"Most reported category: {categories.index[0]}"
            )

    if "location" in df.columns:
        locations = df["location"].dropna().value_counts()
        if not locations.empty:
            insights.append(
                f"Most reported location: {locations.index[0]}"
            )

    monthly_stats = get_time_stats(df)
    if not monthly_stats.empty:
        insights.append(
            f"Busiest reporting month: {monthly_stats.idxmax()}"
        )

    return insights

def get_category_chart(df):
    return df["category"].value_counts()

def get_status_chart(df):
    return df["status"].value_counts()

def get_time_stats(df):
    return df.dropna(subset = ["date"]).groupby(df["date"].dt.to_period("M")).size()
    
if __name__ == "__main__":
    df = create_dataframe(load_items())
    df = clean_data(df)

    print("\nData Quality Report: ", get_data_quality_report(df))
    print("Total reports: ", get_total_reports(df))
    print("\nCategory statistics: ", get_category_stats(df))
    print("\nLocation statistics: ", get_location_stats(df))
    print("\nStatus statistics: ", get_status_stats(df))
    print("\nMatch rate: ", get_match_rate(df))
    print("\nClousure rate: ", get_closure_rate(df))
    print("\nMonthly statistics: ", get_time_stats(df))
    print("\nInsights: ", get_insights(df))

    category_data, status_data, time_data = get_chart_data(df)

    print("\nCategory chart data: ", category_data)
    print("\nStatus chart data: ", status_data)
    print("\nTime chart data: ", time_data)

    print("\nCategory Chart: ", get_category_chart(df))
    print("\nStatus Chart: ", get_status_chart(df))
    print("\nTime Chart: ", time_data)
 