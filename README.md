# Global Patent Intelligence Data Pipeline

A full data engineering pipeline that collects, cleans, stores, and analyzes
real-world patent data from the USPTO PatentsView dataset.

## Project Structure

```
bigdata/
├── data/
│   └── raw/              # Raw TSV files from USPTO (not pushed to GitHub)
├── scripts/
│   ├── load_data.py      # Load raw TSV files
│   ├── clean_data.py     # Clean and export CSVs
│   ├── load_to_db.py     # Load cleaned data into SQLite
│   ├── queries.py        # Run all 7 SQL queries
│   └── report.py         # Generate console, CSV and JSON reports
├── sql/
│   └── schema.sql        # Database schema
├── reports/              # Generated output files
├── database/             # SQLite database (not pushed to GitHub)
└── README.md
```

## Data Source

USPTO PatentsView Granted Patent Disambiguated Data  
https://data.uspto.gov/bulkdata/datasets/pvgpatdis

Files used:
- g_patent.tsv
- g_inventor_disambiguated.tsv
- g_assignee_disambiguated.tsv
- g_patent_abstract.tsv
- g_location_disambiguated.tsv

## How to Reproduce

### 1. Clone the repo
```
git clone https://github.com/Modestnakiroya/bigdata.git
cd bigdata
```

### 2. Install dependencies
```
pip install pandas
```

### 3. Download the data
Download the TSV files from the USPTO link above and place them in `data/raw/`

### 4. Run the pipeline in order
```
python scripts/clean_data.py
python scripts/load_to_db.py
python scripts/queries.py
python scripts/report.py
```

## Results



### Top Inventors
| Rank | Name | Patents |
|------|------|---------|
| 1 | Shunpei Yamazaki | 6,809 |
| 2 | Kia Silverbrook | 4,801 |
| 3 | Tao Luo | 4,493 |

### Top Companies
| Rank | Company | Patents |
|------|---------|---------|
| 1 | Samsung Display Co. | 599,698 |
| 2 | IBM | 562,152 |
| 3 | Canon | 218,847 |

### Top Countries
| Rank | Country | Patents |
|------|---------|---------|
| 1 | US | 5,152,235 |
| 2 | JP | 1,596,388 |
| 3 | DE | 632,808 |

## Technologies Used

- **Python** — data loading and scripting
- **pandas** — data cleaning and transformation
- **SQLite** — database storage and querying
- **SQL** — analytical queries including CTEs and window functions
- **GitHub** — version control and reproducibility