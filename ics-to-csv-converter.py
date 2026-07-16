#!/usr/bin/env python3

import csv
import os
import sys
from pathlib import Path
from icalendar import Calendar
from icalendar.prop import vDatetime, vDate, vText, vRecur
import datetime


def safe_convert_to_ical(value):
    """Safely convert any value to iCal bytes format."""
    try:
        if hasattr(value, 'to_ical'):
            return value.to_ical()
        elif isinstance(value, list):
            results = []
            for item in value:
                if hasattr(item, 'to_ical'):
                    results.append(item.to_ical())
                else:
                    results.append(str(item).encode('utf-8'))
            return b','.join(results) if results else b''
        else:
            return str(value).encode('utf-8')
    except:
        return str(value).encode('utf-8')


def decode_ical_string(value):
    """Safely decode iCal bytes or strings to UTF-8."""
    if value is None:
        return ''
    
    try:
        if isinstance(value, bytes):
            for encoding in ['utf-8', 'windows-1251', 'iso-8859-5', 'cp1251']:
                try:
                    return value.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return value.decode('utf-8', errors='replace')
        elif isinstance(value, str):
            return value
        elif isinstance(value, list):
            return ', '.join(str(v) for v in value if v is not None)
        else:
            return str(value)
    except:
        return str(value)


def decode_escaped_text(text):
    """Decode escaped characters in iCalendar text."""
    if not text:
        return text
    
    text = text.replace('\\n', '\n')
    text = text.replace('\\N', '\n')
    text = text.replace('\\,', ',')
    text = text.replace('\\;', ';')
    text = text.replace('\\\\', '\\')
    text = text.replace('\\"', '"')
    text = text.replace('\\t', '\t')
    text = text.replace('\\T', '\t')
    
    return text


def clean_for_csv(text):
    """Clean text for CSV export."""
    if not text:
        return ''
    
    if not isinstance(text, str):
        text = str(text)
    
    # Remove null characters
    text = text.replace('\x00', '')
    
    # Normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove any non-printable characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def format_datetime_property(dt_property):
    """Format datetime property with timezone awareness."""
    if dt_property is None:
        return ''
    
    try:
        if isinstance(dt_property, list):
            dates = []
            for item in dt_property:
                dates.append(format_datetime_property(item))
            return ', '.join(dates)
        
        if hasattr(dt_property, 'dt'):
            dt = dt_property.dt
            if isinstance(dt, datetime.datetime):
                if dt.tzinfo:
                    return dt.isoformat()
                else:
                    return dt.isoformat() + 'Z'
            else:
                return str(dt)
        elif isinstance(dt_property, datetime.datetime):
            if dt_property.tzinfo:
                return dt_property.isoformat()
            else:
                return dt_property.isoformat() + 'Z'
        else:
            return str(dt_property)
    except:
        return str(dt_property)


def parse_rrule(rrule_value):
    """Parse RRULE into separate fields."""
    result = {
        "RECURRENCE_TYPE": "",
        "INTERVAL": "",
        "BYDAY": "",
        "COUNT": "",
        "UNTIL": "",
        "WKST": "",
    }

    if not rrule_value:
        return result

    try:
        if isinstance(rrule_value, list):
            rrule_value = rrule_value[0] if rrule_value else ''
        
        if hasattr(rrule_value, 'to_ical'):
            rrule_str = decode_ical_string(rrule_value.to_ical())
        else:
            rrule_str = str(rrule_value)

        rrule_str = rrule_str.replace('\r', '').replace('\n', '')
        
        parts = rrule_str.split(';')
        
        for part in parts:
            if '=' not in part:
                continue
            
            key, value = part.split('=', 1)
            
            if key == 'FREQ':
                result['RECURRENCE_TYPE'] = value
            elif key in result:
                result[key] = value
                
    except Exception as e:
        pass

    return result


def parse_ics_with_icalendar(filepath):
    """Parse ICS file using icalendar library."""
    try:
        with open(filepath, 'rb') as f:
            cal = Calendar.from_ical(f.read())
    except UnicodeDecodeError:
        raise RuntimeError("The file is not UTF-8 encoded or is corrupted.")
    except FileNotFoundError:
        raise RuntimeError("ICS file was not found.")
    except PermissionError:
        raise RuntimeError("Permission denied while opening the file.")
    except Exception as e:
        raise RuntimeError(f"Error parsing ICS file: {str(e)}")

    records = []

    for component in cal.walk():
        if component.name == 'VCALENDAR':
            continue
        if component.name == 'VTIMEZONE':
            continue

        # Initialize record with all possible fields
        record = {
            'COMPONENT': component.name,
            'SUMMARY': '',
            'DESCRIPTION': '',
            'LOCATION': '',
            'DTSTART': '',
            'DTEND': '',
            'DUE': '',
            'RRULE': '',
            'RECURRENCE_TYPE': '',
            'INTERVAL': '',
            'BYDAY': '',
            'COUNT': '',
            'UNTIL': '',
            'WKST': '',
            'IS_RECURRING': 'No',
            'STATUS': '',
            'CLASS': '',
            'TRANSP': '',
            'PRIORITY': '',
            'CREATED': '',
            'DTSTAMP': '',
            'LAST_MODIFIED': '',
            'SEQUENCE': '',
            'TIMEZONE': '',
            'ATTENDEE': '',
            'CATEGORIES': '',
            'RESOURCES': '',
            'URL': '',
            'UID': '',
            'ORGANIZER': '',
            'GOOGLE_TASKS': '',
            'GOOGLE_CALENDAR': '',
        }
        
        # Get all properties from the component
        for prop_name in component.keys():
            prop_value = component.get(prop_name)
            
            if prop_value is None:
                continue
            
            # Handle different property types
            if prop_name == 'SUMMARY':
                text = decode_ical_string(safe_convert_to_ical(prop_value))
                text = decode_escaped_text(text)
                record['SUMMARY'] = clean_for_csv(text)
                
            elif prop_name == 'DESCRIPTION':
                text = decode_ical_string(safe_convert_to_ical(prop_value))
                text = decode_escaped_text(text)
                record['DESCRIPTION'] = clean_for_csv(text)
                
            elif prop_name == 'LOCATION':
                text = decode_ical_string(safe_convert_to_ical(prop_value))
                text = decode_escaped_text(text)
                record['LOCATION'] = clean_for_csv(text)
                
            elif prop_name in ['DTSTART', 'DTEND', 'DUE', 'CREATED', 'DTSTAMP', 'LAST_MODIFIED']:
                record[prop_name] = format_datetime_property(prop_value)
                
            elif prop_name == 'RRULE':
                rrule_info = parse_rrule(prop_value)
                record.update(rrule_info)
                record['IS_RECURRING'] = 'Yes' if rrule_info.get('RECURRENCE_TYPE') else 'No'
                raw_value = safe_convert_to_ical(prop_value)
                record['RRULE'] = decode_ical_string(raw_value)
                
            elif prop_name in ['ATTENDEE', 'CATEGORIES', 'RESOURCES']:
                if isinstance(prop_value, list):
                    values = []
                    for item in prop_value:
                        if hasattr(item, 'to_ical'):
                            values.append(decode_ical_string(item.to_ical()))
                        else:
                            values.append(str(item))
                    record[prop_name] = ', '.join(values)
                elif hasattr(prop_value, 'to_ical'):
                    record[prop_name] = decode_ical_string(prop_value.to_ical())
                else:
                    record[prop_name] = str(prop_value)
                    
            elif prop_name == 'SEQUENCE':
                record['SEQUENCE'] = str(prop_value)
                
            elif prop_name == 'UID':
                record['UID'] = str(prop_value)
                
            elif prop_name == 'STATUS':
                record['STATUS'] = str(prop_value)
                
            elif prop_name == 'CLASS':
                record['CLASS'] = str(prop_value)
                
            elif prop_name == 'TRANSP':
                record['TRANSP'] = str(prop_value)
                
            elif prop_name == 'ORGANIZER':
                if hasattr(prop_value, 'to_ical'):
                    record['ORGANIZER'] = decode_ical_string(prop_value.to_ical())
                else:
                    record['ORGANIZER'] = str(prop_value)
                    
            elif prop_name.startswith('X-GOOGLE-'):
                key = prop_name.replace('X-GOOGLE-', '')
                if hasattr(prop_value, 'to_ical'):
                    record[f'GOOGLE_{key}'] = decode_ical_string(prop_value.to_ical())
                else:
                    record[f'GOOGLE_{key}'] = str(prop_value)

        # Extract timezone from DTSTART if available
        if 'DTSTART' in record and record['DTSTART']:
            try:
                dtstart = component.get('DTSTART')
                if hasattr(dtstart, 'dt') and hasattr(dtstart.dt, 'tzinfo'):
                    tz = dtstart.dt.tzinfo
                    if tz:
                        if hasattr(tz, 'zone'):
                            record['TIMEZONE'] = tz.zone
                        elif hasattr(tz, 'key'):
                            record['TIMEZONE'] = tz.key
                        else:
                            record['TIMEZONE'] = str(tz)
                elif hasattr(dtstart, 'dt') and isinstance(dtstart.dt, datetime.date) and not isinstance(dtstart.dt, datetime.datetime):
                    record['TIMEZONE'] = 'ALL-DAY'
            except:
                pass

        records.append(record)

    return records


def export_csv(records, output_file):
    """Export records to CSV with strict column ordering."""
    if not records:
        raise RuntimeError("No calendar events/tasks were found.")

    # Define EXACT column order - this never changes
    columns = [
        'COMPONENT',
        'SUMMARY',
        'DESCRIPTION',
        'LOCATION',
        'DTSTART',
        'DTEND',
        'DUE',
        'RRULE',
        'RECURRENCE_TYPE',
        'INTERVAL',
        'BYDAY',
        'COUNT',
        'UNTIL',
        'WKST',
        'IS_RECURRING',
        'STATUS',
        'CLASS',
        'TRANSP',
        'PRIORITY',
        'CREATED',
        'DTSTAMP',
        'LAST_MODIFIED',
        'SEQUENCE',
        'TIMEZONE',
        'ATTENDEE',
        'CATEGORIES',
        'RESOURCES',
        'URL',
        'UID',
        'ORGANIZER',
        'GOOGLE_TASKS',
        'GOOGLE_CALENDAR',
    ]

    try:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(
                csvfile,
                quoting=csv.QUOTE_ALL,
                quotechar='"',
                doublequote=True,
                delimiter=','
            )
            
            # Write header
            writer.writerow(columns)
            
            # Write data
            for record in records:
                row = []
                for col in columns:
                    value = record.get(col, '')
                    
                    # Convert to string and clean
                    if value is None:
                        value = ''
                    elif not isinstance(value, str):
                        value = str(value)
                    
                    # Clean the value
                    value = clean_for_csv(value)
                    
                    row.append(value)
                
                writer.writerow(row)
                
    except PermissionError:
        raise RuntimeError(
            "Cannot write the CSV file. It may already be open in another program."
        )


def main():
    print("ICS → CSV Converter (Excel Compatible)")
    print("-" * 50)

    if len(sys.argv) > 1:
        ics_file = sys.argv[1]
    else:
        ics_file = input("Enter path to ICS file: ").strip('"')

    if not os.path.exists(ics_file):
        print()
        print("Error: File does not exist.")
        return

    output_file = str(Path(ics_file).with_suffix(".csv"))

    try:
        records = parse_ics_with_icalendar(ics_file)
        export_csv(records, output_file)

        # Statistics
        total_count = len(records)
        recurring_count = sum(1 for r in records if r.get('IS_RECURRING') == 'Yes')
        
        comp_counts = {}
        for r in records:
            comp = r.get('COMPONENT', 'UNKNOWN')
            comp_counts[comp] = comp_counts.get(comp, 0) + 1

        print()
        print("✅ Conversion completed successfully!")
        print(f"📊 Total records    : {total_count}")
        print(f"🔄 Recurring items  : {recurring_count}")
        print(f"📁 Components       : {', '.join(f'{k}={v}' for k, v in comp_counts.items())}")
        print(f"💾 CSV file         : {output_file}")
        
        print("\n📌 Excel Import Instructions:")
        print("1. Open Excel")
        print("2. Go to Data → From Text/CSV")
        print("3. Select the CSV file")
        print("4. In the preview, set:")
        print("   - File Origin: 65001: UTF-8")
        print("   - Delimiter: Comma")
        print("5. Click Load")
        print("\n💡 All fields are quoted and column order is fixed.")
        
    except Exception as e:
        print()
        print("❌ An error occurred during conversion.")
        print(f"Reason: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()