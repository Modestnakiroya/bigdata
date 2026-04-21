import pandas as pd

# Load patent data
patent_df = pd.read_csv("data/raw/g_patent.tsv", sep="\t", nrows=1000000)

# Load inventor data
inventor_df = pd.read_csv("data/raw/g_inventor_disambiguated.tsv", sep="\t")

# Load assignee (company) data
assignee_df = pd.read_csv("data/raw/g_assignee_disambiguated.tsv", sep="\t")

# Load abstract data
abstract_df = pd.read_csv("data/raw/g_patent_abstract.tsv", sep="\t", nrows=1000000)

# Load location data (optional)
location_df = pd.read_csv("data/raw/g_location_disambiguated.tsv", sep="\t")

# Print summaries
print("\nPATENTS:")
print(patent_df.head())

print("\nINVENTORS:")
print(inventor_df.head())

print("\nASSIGNEES:")
print(assignee_df.head())

print("\nABSTRACTS:")
print(abstract_df.head())

print("\nLOCATIONS:")
print(location_df.head())

print("\nPATENTS columns:", patent_df.columns.tolist())
print("INVENTORS columns:", inventor_df.columns.tolist())
print("ASSIGNEES columns:", assignee_df.columns.tolist())
print("LOCATIONS columns:", location_df.columns.tolist())