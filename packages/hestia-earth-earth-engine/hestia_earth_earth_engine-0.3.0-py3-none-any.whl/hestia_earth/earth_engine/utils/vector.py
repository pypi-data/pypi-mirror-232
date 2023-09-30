from io import BytesIO
import warnings
from shapely.geometry import shape, Point
import geopandas as gpd

from .storage import load_from_storage
from .gee import load_region_geometry, _id_to_level

DEFAULT_CRS = 'EPSG:4326'
GEOMETRY_BY_TYPE = {
    'FeatureCollection': lambda x: _get_geometry_by_type(x.get('features')[0]),
    'GeometryCollection': lambda x: _get_geometry_by_type(x.get('geometries')[0]),
    'Feature': lambda x: x.get('geometry'),
    'Polygon': lambda x: x,
    'MultiPolygon': lambda x: x
}


def _get_geometry_by_type(geojson): return GEOMETRY_BY_TYPE[geojson.get('type')](geojson)


def _build_frames(collections: list):
    geodataframes = []
    field_names = []

    for collection in collections:
        # TODO: check if zip exists, else defaults to shp
        data = load_from_storage(f"{collection.get('collection')}.zip")
        gdf = gpd.read_file(BytesIO(data))
        geodataframes.append(gdf)
        fields = collection.get('fields')
        field_names.extend(fields if isinstance(fields, list) else [fields])

    return geodataframes, field_names


# Define a function to process multiple GeoDataFrames and fields
def _process_coordinates(geodataframes, coordinates_list, field_names):
    results = []
    for i, gdf in enumerate(geodataframes):
        # Extract coordinates from the coordinates_list
        for coord in coordinates_list:
            point = Point(coord.get('longitude'), coord.get('latitude'))
            intersection = gdf[gdf.intersects(point)]

            if not intersection.empty:
                field = field_names[i]
                results.extend(intersection[field].values)
    return results  # Return the results list


def run_by_coordinates(collections: list, coordinates: list):
    geodataframes, field_names = _build_frames(collections)
    return _process_coordinates(geodataframes, coordinates, field_names)


def _calculate_intersection_area(gdf, dataframe):
    # Intersect the two GeoDataFrames and calculate the area of each intersection
    intersection = gpd.overlay(gdf, dataframe, how='intersection')

    # Suppress the warning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        intersection['area_intersection'] = intersection['geometry'].area

    return intersection


# Define a function to find the largest area and corresponding field value
def _find_largest_area_field_value(intersection, field_name):
    # Sort the intersection by the largest area
    sorted_intersection = intersection.sort_values(by='area_intersection', ascending=False)
    return sorted_intersection.iloc[0][field_name] if field_name else None


def _procress_dataframes(geodataframes: list, field_names: list, dataframes: list):
    results = []

    for i, gdf in enumerate(geodataframes):
        field_name = field_names[i] if i < len(field_names) else None

        for dataframe in dataframes:
            intersection = _calculate_intersection_area(gdf, dataframe)
            largest_area_field_value = _find_largest_area_field_value(intersection, field_name)

            if largest_area_field_value is not None:
                results.append(largest_area_field_value)

    return results


def _load_geometries_from_boundaries(boundaries: list):
    geometries = [
        _get_geometry_by_type(boundary) for boundary in boundaries
    ]
    return [
        gpd.GeoDataFrame(geometry=[shape(geometry)], crs=DEFAULT_CRS) for geometry in geometries
    ]


# Define a function to process multiple GeoDataFrames and fields
def run_by_boundaries(collections: list, boundaries: list):
    geodataframes, field_names = _build_frames(collections)
    dataframes = _load_geometries_from_boundaries(boundaries)
    return _procress_dataframes(geodataframes, field_names, dataframes)


def _load_gadm_boundary(gadm_id: str):
    # Count the number of dots in the GADM ID name
    gadm_level = _id_to_level(gadm_id)
    country_code = gadm_id.replace('GADM-', '').split('.')[0]

    # get the appropriate field
    field = f"GID_{gadm_level}"

    # loads from individual country shapefiles
    shapefile_bytes = load_from_storage(f'gadm/gadm36_{country_code}_shp.zip')
    gdf = gpd.read_file(BytesIO(shapefile_bytes), layer=f"gadm36_{country_code}_{gadm_level}")
    gdf_gadm = gdf[gdf[field] == gadm_id.replace('GADM-', '')]
    # make sure crs is set
    gdf_gadm.crs = gdf_gadm.crs or DEFAULT_CRS
    return gdf_gadm


def run_by_gadm_ids(collections: list, gadm_ids: str, use_gee: bool = False):
    geodataframes, field_names = _build_frames(collections)
    # TODO: this does not guarantee the order of the results
    # gadm_ids = list(set(gadm_ids))

    dataframes = _load_geometries_from_boundaries(list(map(load_region_geometry, gadm_ids))) if use_gee else \
        list(map(_load_gadm_boundary, gadm_ids))

    return _procress_dataframes(geodataframes, field_names, dataframes)
