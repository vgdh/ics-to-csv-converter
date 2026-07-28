# ICS to CSV Converter
Convert Google iCalendar (.ics) files to Excel-compatible CSV format with full Unicode support.

## 📋 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Excel Import Guide](#-excel-import-guide)
- [Supported Properties](#-supported-properties)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

- ✅ **Preserves all ICS properties** - No data loss during conversion
- ✅ **Full Unicode support** - Handles Cyrillic, Chinese, Arabic, and all UTF-8 characters
- ✅ **Recurring events** - Properly parses RRULE (FREQ, INTERVAL, BYDAY, COUNT, UNTIL, etc.)
- ✅ **Google Calendar & Tasks** - Supports Google-specific properties
- ✅ **Multiline text** - Preserves descriptions with multiple lines
- ✅ **Timezone aware** - Correctly parses and displays timezone information
- ✅ **Excel compatible** - Outputs CSV with proper quoting for Excel import
- ✅ **Multiple fields** - Handles multiple ATTENDEE, EXDATE, CATEGORIES entries
- ✅ **Escaped characters** - Decodes `\n`, `\,`, `\;`, `\\`, `\"`
- ✅ **All-day events** - Properly identifies and handles all-day events
- ✅ **Event status** - Preserves CONFIRMED, CANCELLED, TENTATIVE status

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install icalendar pytz python-dateutil
```

### Clone the Repository

```bash
git clone https://github.com/yourusername/ics-to-csv-converter.git
cd ics-to-csv-converter
```

## 🚀 Usage

### Basic Usage

```bash
python ics_to_csv.py your_calendar.ics
```

### Interactive Mode

```bash
python ics_to_csv.py
# Then enter the path to your ICS file when prompted
```

### Output

The script will create a CSV file with the same name as your ICS file:
- `your_calendar.ics` → `your_calendar.csv`

### Command Line Options

```bash
# With a specific file
python ics_to_csv.py ~/Downloads/calendar.ics

# With a file in the current directory
python ics_to_csv.py calendar.ics

# Interactive prompt
python ics_to_csv.py
```

## 📊 Excel Import Guide

### Method 1: Data Tab (Recommended)

1. Open Excel
2. Go to **Data** → **From Text/CSV**
3. Select your CSV file
4. In the preview window, set:
   - **File Origin**: `65001: UTF-8`
   - **Delimiter**: `Comma`
   - **Data Type Detection**: Based on first 200 rows
5. Click **Load**

### Method 2: Legacy Import Wizard

1. Open Excel
2. Go to **Data** → **Get External Data** → **From Text**
3. Select your CSV file
4. Choose **Delimited**
5. Select **Comma** as delimiter
6. Set **File Origin** to `65001: UTF-8`
7. Click **Finish**

### Method 3: Google Sheets

1. Open Google Sheets
2. Go to **File** → **Import**
3. Select **Upload** and choose your CSV file
4. Select **Replace current sheet** or **New sheet**
5. Choose **Comma** as separator
6. Click **Import data**

## 📋 Supported Properties

| Category | Properties |
|----------|------------|
| **Core** | COMPONENT, SUMMARY, DESCRIPTION, LOCATION |
| **Dates** | DTSTART, DTEND, DUE, CREATED, DTSTAMP, LAST-MODIFIED |
| **Recurrence** | RRULE, RECURRENCE_TYPE, INTERVAL, BYDAY, COUNT, UNTIL, WKST |
| **Status** | IS_RECURRING, STATUS, CLASS, TRANSP, PRIORITY |
| **Participants** | ATTENDEE, ORGANIZER, RESOURCES |
| **Classification** | CATEGORIES, URL, UID |
| **Google** | GOOGLE_TASKS, GOOGLE_CALENDAR |
| **Time** | TIMEZONE |

### RRULE Parsing

The converter extracts the following recurrence rules:
- `FREQ`: DAILY, WEEKLY, MONTHLY, YEARLY
- `INTERVAL`: Frequency interval
- `BYDAY`: Days of the week (MO, TU, WE, TH, FR, SA, SU)
- `COUNT`: Number of occurrences
- `UNTIL`: End date
- `WKST`: Week start day

## 💡 Examples

### Input (ICS)

```
BEGIN:VEVENT
SUMMARY:Team Meeting
DESCRIPTION:Weekly team sync\\nDiscuss project status
DTSTART:20240115T100000Z
DTEND:20240115T110000Z
RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO
LOCATION:Conference Room A
END:VEVENT
```

### Output (CSV)

```csv
"COMPONENT","SUMMARY","DESCRIPTION","DTSTART","DTEND","RRULE","RECURRENCE_TYPE","INTERVAL","BYDAY","IS_RECURRING"
"VEVENT","Team Meeting","Weekly team sync\nDiscuss project status","2024-01-15T10:00:00Z","2024-01-15T11:00:00Z","FREQ=WEEKLY;INTERVAL=1;BYDAY=MO","WEEKLY","1","MO","Yes"
```

## 🔧 Troubleshooting

### Common Issues

#### "UnicodeDecodeError" or garbled text
- The file might not be UTF-8 encoded
- Try saving the ICS file with UTF-8 encoding
- The script supports multiple encodings (UTF-8, Windows-1251, ISO-8859-5)

#### "Permission denied" error
- Close the CSV file if it's open in Excel or another program
- Make sure you have write permissions in the output directory

#### CSV imports with wrong data alignment
- Make sure to select `Comma` as delimiter in Excel
- Set File Origin to `65001: UTF-8`
- All fields are quoted to handle special characters

#### Missing fields in output
- Some fields may be empty if not present in the original ICS
- The script preserves all existing fields from the ICS

### Excel Display Issues

If text appears with `#` symbols or weird characters:
1. Try importing as CSV with UTF-8 encoding
2. Use Excel's "From Text/CSV" option instead of double-clicking
3. Make sure to select `65001: UTF-8` as the file origin

---

Made with ❤️ for the open-source community
