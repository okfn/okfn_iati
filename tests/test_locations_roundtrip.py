"""Round-trip tests for locations.csv <-> <location> (IATI 2.03).

The fixture ``tests/sample_locations.csv`` has two rows for each way of
expressing a location supported by the standard:

- whole country by ISO 3166-1 alpha-2 code (location-id vocabulary A4)
- administrative area identified by a gazetteer code (location-id G1 + administrative)
- exact point (lat/lng, exactness 1) inside an administrative area
- approximate point (lat/lng, exactness 2) for a city
- named region without codes or coordinates
- gazetteer identifiers (OpenStreetMap G2 / Geonames G1)

The same rows are published as the example table in the BCIE documentation.
"""
import csv
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from okfn_iati import IatiMultiCsvConverter, Location, LocationIdentifier
from okfn_iati.activities.process_csv.builders import build_location
from okfn_iati.activities.process_xml.extractors import extract_location_data
from okfn_iati.csv_validators.locations_validator import LocationsCsvValidator
from okfn_iati.csv_validators.models import ErrorCode, ValidationLevel
from okfn_iati.xml_generator import IatiXmlGenerator

HERE = Path(__file__).parent.resolve()
SAMPLE_LOCATIONS = HERE / "sample_locations.csv"
WORLDBANK_XML = HERE.parent / "data-samples" / "xml" / "worldbank-679.xml"

LOCATION_COLUMNS = IatiMultiCsvConverter.csv_files['locations']['columns']
ACTIVITY_ID = "XM-DAC-46008-cfa012402"


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, columns, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in columns})


def write_minimal_folder(folder: Path, location_rows):
    """Write the smallest CSV folder that validates against the 2.03 XSD."""
    folder.mkdir(parents=True, exist_ok=True)
    files = IatiMultiCsvConverter.csv_files
    write_csv(folder / files['activities']['filename'], files['activities']['columns'], [{
        'activity_identifier': ACTIVITY_ID,
        'title': 'Programa de infraestructura social',
        'title_lang': 'es',
        'description': 'Actividad de ejemplo con ubicaciones',
        'description_lang': 'es',
        'activity_status': '2',
        'default_currency': 'USD',
        'xml_lang': 'es',
        'reporting_org_ref': 'XM-DAC-46008',
        'reporting_org_name': 'BCIE',
        'reporting_org_name_lang': 'es',
        'reporting_org_type': '40',
        'planned_start_date': '2024-01-01',
        'recipient_country_code': 'HN',
        'recipient_country_percentage': '100',
    }])
    write_csv(folder / files['participating_orgs']['filename'], files['participating_orgs']['columns'], [{
        'activity_identifier': ACTIVITY_ID,
        'org_ref': 'XM-DAC-46008',
        'org_name': 'BCIE',
        'org_name_lang': 'es',
        'org_type': '40',
        'role': '1',
    }])
    write_csv(folder / files['sectors']['filename'], files['sectors']['columns'], [{
        'activity_identifier': ACTIVITY_ID,
        'sector_code': '14030',
        'vocabulary': '1',
        'percentage': '100',
    }])
    write_csv(folder / files['locations']['filename'], LOCATION_COLUMNS, location_rows)


def rows_by_ref(rows):
    return {r['location_ref']: r for r in rows}


class TestSampleLocationsFixture(unittest.TestCase):
    """The fixture itself must be valid and cover every location kind."""

    def setUp(self):
        self.rows = read_rows(SAMPLE_LOCATIONS)

    def test_fixture_has_two_rows_per_kind(self):
        self.assertEqual(len(self.rows), 12)
        kinds = {
            'iso_country': lambda r: r['location_id_vocabulary'] == 'A4',
            'admin_area_by_code': lambda r: r['location_id_vocabulary'] == 'G1' and r['feature_designation'] == 'ADM1',
            'exact_point': lambda r: r['latitude'] and r['exactness'] == '1',
            'approx_point': lambda r: r['latitude'] and r['exactness'] == '2',
            'name_only': lambda r: not r['latitude'] and not r['location_id_code'] and not r['administrative_code'],
            'gazetteer': lambda r: r['location_id_vocabulary'] in ('G1', 'G2') and r['location_class'] == '2',
        }
        for kind, pred in kinds.items():
            self.assertEqual(len([r for r in self.rows if pred(r)]), 2, kind)

    def test_fixture_passes_csv_validator(self):
        result = LocationsCsvValidator().validate(SAMPLE_LOCATIONS)
        self.assertTrue(result.is_valid, result.errors)
        warnings = [i for i in result.issues if i.level == ValidationLevel.WARNING]
        self.assertEqual(warnings, [], [str(w) for w in warnings])


class TestCsvToXmlToCsvRoundtrip(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_every_location_column_survives_csv_xml_csv(self):
        original = read_rows(SAMPLE_LOCATIONS)
        folder_a = self.tmp / "a"
        write_minimal_folder(folder_a, original)

        out_xml = self.tmp / "out.xml"
        converter = IatiMultiCsvConverter()
        ok = converter.csv_folder_to_xml(str(folder_a), str(out_xml), validate_output=True)
        self.assertTrue(ok, "csv_folder_to_xml failed or produced XSD-invalid XML")

        folder_b = self.tmp / "b"
        self.assertTrue(converter.xml_to_csv_folder(str(out_xml), str(folder_b)))
        recovered = rows_by_ref(read_rows(folder_b / "locations.csv"))

        self.assertEqual(len(recovered), len(original))
        for row in original:
            rec = recovered[row['location_ref']]
            for col in LOCATION_COLUMNS:
                self.assertEqual(
                    row[col], rec.get(col, ''),
                    f"{row['location_ref']}: column '{col}' changed after round-trip"
                )

    def test_generated_xml_uses_203_child_elements(self):
        folder = self.tmp / "a"
        write_minimal_folder(folder, read_rows(SAMPLE_LOCATIONS))
        out_xml = self.tmp / "out.xml"
        self.assertTrue(IatiMultiCsvConverter().csv_folder_to_xml(str(folder), str(out_xml), validate_output=True))

        root = ET.parse(out_xml).getroot()
        locations = {loc.get('ref'): loc for loc in root.iter('location')}
        self.assertEqual(len(locations), 12)

        country = locations['LOC-PAIS-HN']
        self.assertEqual(country.find('location-reach').get('code'), '1')
        self.assertEqual(country.find('location-id').get('vocabulary'), 'A4')
        self.assertEqual(country.find('location-id').get('code'), 'HN')
        self.assertEqual(country.find('exactness').get('code'), '1')
        self.assertEqual(country.find('location-class').get('code'), '1')
        self.assertEqual(country.find('feature-designation').get('code'), 'PCLI')
        self.assertIsNone(country.find('point'))
        self.assertIsNone(country.find('administrative'))
        # none of these may leak back in as attributes of <location>
        for attr in ('reach', 'exactness', 'class', 'feature-designation'):
            self.assertIsNone(country.get(attr))

        point = locations['LOC-PT-HOSP']
        self.assertEqual(point.find('point').get('srsName'), 'http://www.opengis.net/def/crs/EPSG/0/4326')
        self.assertEqual(point.find('point/pos').text, '14.0891 -87.1650')
        admin = point.find('administrative')
        self.assertEqual(admin.attrib, {'vocabulary': 'G1', 'code': '3608992', 'level': '1'})
        self.assertEqual(point.find('activity-description/narrative').text, 'Ampliacion de la sala de emergencias')

        beneficiaries = locations['LOC-REG-CS']
        self.assertEqual(beneficiaries.find('location-reach').get('code'), '2')
        self.assertEqual(beneficiaries.find('feature-designation').get('code'), 'RGN')
        self.assertIsNone(beneficiaries.find('point'))
        self.assertIsNone(beneficiaries.find('location-id'))

        osm = locations['LOC-OSM-PC']
        self.assertEqual(osm.find('location-id').attrib, {'vocabulary': 'G2', 'code': 'relation/1234567'})


class TestXmlToCsvToXmlRoundtrip(unittest.TestCase):
    """Real-world file: World Bank activities with reach/exactness/class as child elements."""

    def setUp(self):
        if not WORLDBANK_XML.exists():
            self.skipTest(f"missing {WORLDBANK_XML}")
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_child_elements_are_extracted_and_preserved(self):
        converter = IatiMultiCsvConverter()
        folder_a = self.tmp / "a"
        self.assertTrue(converter.xml_to_csv_folder(str(WORLDBANK_XML), str(folder_a)))
        rows_a = read_rows(folder_a / "locations.csv")
        self.assertTrue(rows_a)

        # These used to be lost because they were read as <location> attributes
        self.assertTrue(any(r['location_reach'] for r in rows_a), "location_reach not extracted")
        self.assertTrue(any(r['exactness'] for r in rows_a), "exactness not extracted")
        self.assertTrue(any(r['location_class'] for r in rows_a), "location_class not extracted")

        # The sample has a negative budget that the model rejects; budgets are
        # irrelevant here, so drop that file before going back to XML.
        folder_a2 = self.tmp / "a2"
        shutil.copytree(folder_a, folder_a2)
        (folder_a2 / "budgets.csv").unlink()
        mid_xml = self.tmp / "mid.xml"
        self.assertTrue(converter.csv_folder_to_xml(str(folder_a2), str(mid_xml), validate_output=True))
        folder_b = self.tmp / "b"
        self.assertTrue(converter.xml_to_csv_folder(str(mid_xml), str(folder_b)))
        rows_b = read_rows(folder_b / "locations.csv")

        self.assertEqual(len(rows_a), len(rows_b))
        for a, b in zip(rows_a, rows_b):
            self.assertEqual(a, b)


class TestExtractLocationData(unittest.TestCase):

    def test_reads_203_child_elements(self):
        xml = '''
        <location ref="LOC-1">
            <location-reach code="2"/>
            <location-id vocabulary="A4" code="NI"/>
            <name><narrative xml:lang="es">Nicaragua</narrative></name>
            <description><narrative xml:lang="es">Pais</narrative></description>
            <activity-description><narrative xml:lang="es">Obras</narrative></activity-description>
            <administrative vocabulary="G1" level="1" code="3617762"/>
            <point srsName="http://www.opengis.net/def/crs/EPSG/0/4326"><pos>12.1364 -86.2514</pos></point>
            <exactness code="1"/>
            <location-class code="1"/>
            <feature-designation code="PCLI"/>
        </location>'''
        data = extract_location_data(ET.fromstring(xml), "ACT-1")
        self.assertEqual(data, {
            'activity_identifier': 'ACT-1',
            'location_ref': 'LOC-1',
            'location_reach': '2',
            'location_id_vocabulary': 'A4',
            'location_id_code': 'NI',
            'name': 'Nicaragua',
            'name_lang': 'es',
            'description': 'Pais',
            'description_lang': 'es',
            'activity_description': 'Obras',
            'activity_description_lang': 'es',
            'latitude': '12.1364',
            'longitude': '-86.2514',
            'exactness': '1',
            'location_class': '1',
            'feature_designation': 'PCLI',
            'administrative_vocabulary': 'G1',
            'administrative_level': '1',
            'administrative_code': '3617762',
            'administrative_country': '',
        })
        self.assertEqual(set(data), set(LOCATION_COLUMNS))

    def test_tolerates_legacy_attribute_form(self):
        xml = '<location reach="1" exactness="2" class="3" feature-designation="SCH"/>'
        data = extract_location_data(ET.fromstring(xml), "ACT-1")
        self.assertEqual(data['location_reach'], '1')
        self.assertEqual(data['exactness'], '2')
        self.assertEqual(data['location_class'], '3')
        self.assertEqual(data['feature_designation'], 'SCH')

    def test_empty_location(self):
        data = extract_location_data(ET.fromstring('<location/>'), "ACT-1")
        self.assertEqual(set(data), set(LOCATION_COLUMNS))
        self.assertTrue(all(v == '' for k, v in data.items() if k != 'activity_identifier'))


class TestBuildLocation(unittest.TestCase):

    def test_all_columns_mapped(self):
        row = read_rows(SAMPLE_LOCATIONS)[4]  # LOC-PT-HOSP
        loc = build_location(row)
        self.assertEqual(loc.ref, 'LOC-PT-HOSP')
        self.assertEqual(loc.location_reach.value, '1')
        self.assertIsNone(loc.location_id)
        self.assertEqual(loc.name[0].text, 'Hospital Escuela')
        self.assertEqual(loc.name[0].lang, 'es')
        self.assertEqual(loc.activity_description[0].text, 'Ampliacion de la sala de emergencias')
        self.assertEqual(loc.point['pos'], '14.0891 -87.1650')
        self.assertEqual(loc.exactness.value, '1')
        self.assertEqual(loc.location_class, '3')
        self.assertEqual(loc.feature_designation, 'HSP')
        self.assertEqual(loc.administrative, [{'vocabulary': 'G1', 'code': '3608992', 'level': '1'}])

    def test_iso_country_location_id(self):
        loc = build_location({'location_id_vocabulary': 'A4', 'location_id_code': 'HN'})
        self.assertIsInstance(loc.location_id, LocationIdentifier)
        self.assertEqual(loc.location_id.vocabulary, 'A4')
        self.assertEqual(loc.location_id.code, 'HN')

    def test_invalid_vocabulary_raises(self):
        with self.assertRaises(ValueError):
            build_location({'location_id_vocabulary': 'GADM', 'location_id_code': 'HND.8_1'})

    def test_administrative_country_is_not_written(self):
        loc = build_location({
            'administrative_vocabulary': 'A4', 'administrative_code': 'HN', 'administrative_country': 'HN',
        })
        self.assertEqual(loc.administrative, [{'vocabulary': 'A4', 'code': 'HN'}])

    def test_half_coordinates_are_ignored(self):
        loc = build_location({'latitude': '14.0', 'longitude': ''})
        self.assertIsNone(loc.point)

    def test_empty_row_gives_empty_location(self):
        self.assertEqual(build_location({c: '' for c in LOCATION_COLUMNS}), Location())


class TestLocationsValidatorRules(unittest.TestCase):

    def _validate(self, row):
        tmp = Path(tempfile.mkdtemp())
        try:
            path = tmp / "locations.csv"
            base = {'activity_identifier': ACTIVITY_ID}
            base.update(row)
            write_csv(path, LOCATION_COLUMNS, [base])
            return LocationsCsvValidator().validate(path)
        finally:
            shutil.rmtree(tmp)

    def _codes(self, result, level=ValidationLevel.ERROR):
        return [(i.code, i.column_name) for i in result.issues if i.level == level]

    def test_exactness_uses_geographic_exactness_codelist(self):
        self.assertTrue(self._validate({'name': 'X', 'exactness': '2'}).is_valid)
        self.assertIn((ErrorCode.INVALID_ENUM, 'exactness'), self._codes(self._validate({'name': 'X', 'exactness': '3'})))

    def test_location_class_codelist(self):
        self.assertTrue(self._validate({'name': 'X', 'location_class': '4'}).is_valid)
        self.assertIn((ErrorCode.INVALID_ENUM, 'location_class'),
                      self._codes(self._validate({'name': 'X', 'location_class': 'PPL'})))

    def test_feature_designation_codelist(self):
        self.assertTrue(self._validate({'name': 'X', 'feature_designation': 'PPL'}).is_valid)
        self.assertIn((ErrorCode.INVALID_ENUM, 'feature_designation'),
                      self._codes(self._validate({'name': 'X', 'feature_designation': 'NOPE'})))

    def test_administrative_vocabulary_and_level(self):
        self.assertTrue(self._validate({'administrative_vocabulary': 'A3', 'administrative_code': 'HND.8_1',
                                        'administrative_level': '1'}).is_valid)
        codes = self._codes(self._validate({'administrative_vocabulary': 'GADM', 'administrative_code': 'X',
                                            'administrative_level': 'uno'}))
        self.assertIn((ErrorCode.INVALID_ENUM, 'administrative_vocabulary'), codes)
        self.assertIn((ErrorCode.INVALID_INTEGER, 'administrative_level'), codes)

    def test_coordinates_must_come_in_pairs_and_in_range(self):
        self.assertIn((ErrorCode.CUSTOM, 'longitude'), self._codes(self._validate({'latitude': '14.0'})))
        self.assertIn((ErrorCode.CUSTOM, 'latitude'), self._codes(self._validate({'longitude': '-87.0'})))
        self.assertIn((ErrorCode.INVALID_DECIMAL, 'latitude'),
                      self._codes(self._validate({'latitude': '95', 'longitude': '-87.0'})))
        self.assertIn((ErrorCode.INVALID_DECIMAL, 'longitude'),
                      self._codes(self._validate({'latitude': '14', 'longitude': '-187.0'})))

    def test_location_id_and_administrative_pairs(self):
        self.assertIn((ErrorCode.CUSTOM, 'location_id_vocabulary'),
                      self._codes(self._validate({'location_id_code': 'HN'})))
        self.assertIn((ErrorCode.CUSTOM, 'location_id_code'),
                      self._codes(self._validate({'location_id_vocabulary': 'A4'})))
        self.assertIn((ErrorCode.CUSTOM, 'administrative_code'),
                      self._codes(self._validate({'administrative_vocabulary': 'A4'})))

    def test_administrative_country_warns(self):
        result = self._validate({'name': 'X', 'administrative_country': 'HN'})
        self.assertTrue(result.is_valid)
        self.assertIn((ErrorCode.CUSTOM, 'administrative_country'), self._codes(result, ValidationLevel.WARNING))

    def test_location_without_any_content_warns(self):
        result = self._validate({'location_reach': '1'})
        self.assertTrue(result.is_valid)
        self.assertIn((ErrorCode.CUSTOM, None), self._codes(result, ValidationLevel.WARNING))


class TestXmlGeneratorLocation(unittest.TestCase):

    def test_model_to_xml_child_elements(self):
        gen = IatiXmlGenerator()
        activity_el = ET.Element('iati-activity')
        gen._add_location(activity_el, Location(
            ref='R', location_reach='2', location_id=LocationIdentifier(vocabulary='A4', code='GT'),
            exactness='2', location_class='1', feature_designation='PCLI',
            administrative=[{'vocabulary': 'G1', 'code': '3595528', 'level': '0'}],
        ))
        loc = activity_el.find('location')
        self.assertEqual(loc.get('ref'), 'R')
        self.assertEqual(loc.find('location-reach').get('code'), '2')
        self.assertEqual(loc.find('location-id').attrib, {'vocabulary': 'A4', 'code': 'GT'})
        self.assertEqual(loc.find('exactness').get('code'), '2')
        self.assertEqual(loc.find('location-class').get('code'), '1')
        self.assertEqual(loc.find('feature-designation').get('code'), 'PCLI')
        self.assertEqual(loc.find('administrative').attrib, {'vocabulary': 'G1', 'code': '3595528', 'level': '0'})


if __name__ == '__main__':
    unittest.main()
