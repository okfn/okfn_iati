# IATI data samples

Sources of IATI data samples can be found in the following locations:

 - IATI Data Dump https://iati-data-dump.codeforiati.org/ (~700MB compressed)
 - https://github.com/IATI/bulk-data-service/tree/develop/tests/artifacts/iati-xml-files

## CSV base files

Clients can just create CSV files with their data so this library can generate XML/IATI files.  

The file `sample_activities.csv` file contains a sample of the data that can be used to generate IATI XML files.  

The test file `test_csv_to_xml.py` shows you an example on how to load from CSV files and generate IATI XML files.  

The file `tests/test_activities_generated.xml` is the generated XML file from the `sample_activities.csv` file.  

### Notes

Multiple sectors per activity are supported via the multi-CSV approach using `sectors.csv`, where each sector is a separate row linked by `activity_identifier`.

Budget periods spanning more than one year should be split into annual periods, one row per year in `budgets.csv`.
