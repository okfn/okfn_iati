# Activity file samples

Search by file type (activity files): https://iatiregistry.org/dataset/?q=&publisher_source_type=&secondary_publisher=&organization=&publisher_country=&publisher_organization_type=&country=&filetype=Activity.  

## Running tests

Here some real life sample usage to test this library:

```bash
python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/CAF-ActivityFile-2025-10-10.xml data-samples/csv_folders/CAF
# and roll back to test
python scripts/csv_tools.py csv-folder-to-xml data-samples/csv_folders/CAF data-samples/xml/CAF-ActivityFile-2025-10-10-back.xml

python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/iadb-Brazil.xml data-samples/csv_folders/IADBBrasil
python scripts/csv_tools.py csv-folder-to-xml data-samples/csv_folders/IADBBrasil data-samples/xml/iadb-Brazil-back.xml

python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/usaid-798.xml data-samples/csv_folders/usaid-798
python scripts/csv_tools.py csv-folder-to-xml data-samples/csv_folders/usaid-798 data-samples/xml/usaid-798-back.xml
```