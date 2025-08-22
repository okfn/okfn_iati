# Multi CSV samples

This folder contains examples of the multi-CSV structure for IATI data.  
They were generated with commands like

```bash
python scripts/csv_tools.py xml-to-csv-folder data-samples/xml/usaid-bb.xml usaid-bb
python scripts/csv_tools.py xml-to-csv-folder tests/full_xml/test_usaid_generated.xml usaid
```

Each subfolder represents a different dataset, with CSV files organized according to the
[CSV Data Hierarchy Guide](docs/csv_data_hierarchy.md).  
