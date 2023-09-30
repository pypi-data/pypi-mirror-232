import os
import json
from tests.utils import fixtures_path

from hestia_earth.earth_engine.coordinates import run

fixtures_folder = os.path.join(fixtures_path, 'coordinates')


def test_run_raster_by_period():
    with open(os.path.join(fixtures_folder, 'raster-by-period.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert round(results[0], 10) == 1.0355721181


def test_run_raster_by_period_reduce_years():
    with open(os.path.join(fixtures_folder, 'raster-by-period-reduce-years.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert round(results[0], 10) == 1.3133145281


def test_run_raster_by_period_histosol():
    with open(os.path.join(fixtures_folder, 'raster-by-period-histosol.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert round(results[0], 10) == 1.2185599804


def test_run_raster():
    with open(os.path.join(fixtures_folder, 'raster.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert round(results[0], 10) == 81


def test_run_raster_multiple():
    with open(os.path.join(fixtures_folder, 'raster-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert results == [66, 1, 12, 64, 3, 11]


def test_run_vector():
    with open(os.path.join(fixtures_folder, 'vector.json'), encoding='utf-8') as f:
        data = json.load(f)

    results = run(data)
    assert results[0] == '9692'


def test_run_vector_multiple():
    with open(os.path.join(fixtures_folder, 'vector-multiple.json'), encoding='utf-8') as f:
        data = json.load(f)

    values = run(data)
    assert values == ['9135', '9692', 'NT0704', 'NT0704']
