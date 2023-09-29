import csv
import json
import os
from os import listdir
from os.path import join, isfile

from wbparser.main import WBparser


parser = WBparser()
parser.parse_data(ids=[11152183, 87628789], urls=['https://www.wildberries.ru/catalog/155761175/detail.aspx'])


mock_result = [
    {
        'id': '11152183',
        'name': 'Ботинки женские демисезонные натуральная кожа на шнуровке',
        'brand': 'O`SHADE',
        'priceU': 7574,
        'salePriceU': 5529,
        'picsAmt': 16,
        'colors': [{'name': 'черный', 'id': 0}],
        'sizes': ['36', '37', '38', '39', '40', '41', '42', '43'],
        'qty': 566,
        'rating': 4.7,
        'feedbacksAmt': 2055,
        'supplierId': 18744
    }
]


def test_parse_data_by_ids():

    assert parser.result is not None
    assert 11152183 in parser.ids
    assert 87628789 in parser.ids
    assert 'O`SHADE' in parser.brand
    assert 'T.TACCARDI' in parser.brand


def test_parse_data_by_urls():

    assert parser.result is not None
    assert '155761175' in parser.ids
    assert 'Avanti' in parser.brand


def test_save_data_to_json():

    mock_parser = WBparser()
    mock_parser.result = mock_result

    mock_parser.save_data(file_name='testfileJSON')

    assert 'testfileJSON.json' in [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]

    with open('testfileJSON.json', 'r') as f:
        data = json.loads(''.join(f.readlines()))[0]

    assert data['id'] == '11152183'
    assert data['rating'] == 4.7
    assert data['sizes'] == ['36', '37', '38', '39', '40', '41', '42', '43']
    assert data['colors'] == [{'name': 'черный', 'id': 0}]


def test_save_data_to_csv():

    mock_parser = WBparser()
    mock_parser.result = mock_result

    mock_parser.save_data(file_name='testfileCSV', file_format='csv')

    assert 'testfileCSV.csv' in [f for f in listdir(os.getcwd()) if isfile(join(os.getcwd(), f))]

    with open('testfileCSV.csv', mode='r') as f:
        csv_reader = csv.DictReader(f)
        data = [row for row in csv_reader][0]

    assert data['id'] == '11152183'
    assert data['rating'] == '4.7'
    assert data['sizes'] == "['36', '37', '38', '39', '40', '41', '42', '43']"
