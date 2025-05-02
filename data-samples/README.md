# IATI data samples

Sources of IATI data samples can be found in the following locations:

 - IATI Data Dump https://iati-data-dump.codeforiati.org/ (~700MB compressed)
 - https://github.com/IATI/bulk-data-service/tree/develop/tests/artifacts/iati-xml-files

## CSV base files

Clients can just create CSV files with their data so this library can generate XML/IATI files.  

The file `sample_activities.csv` file contains a sample of the data that can be used to generate IATI XML files.  

The test file `test_csv_to_xml.py` shows you an example on how to load from CSV files and generate IATI XML files.  

The file `tests/test_activities_generated.xml` is the generated XML file from the `sample_activities.csv` file.  

### Pending improvements

If we need to include more than one `sector` in the CSV file, we need to add a new column for each sector.  
We now only one `sector` and assign 100% to it.  

The `budget` period can't be more that one year. In those case we will probably need to split the budget in parts in our code.  
Pending to investigate.  
