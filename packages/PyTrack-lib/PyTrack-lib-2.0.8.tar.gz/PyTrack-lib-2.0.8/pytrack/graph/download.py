import requests


def get_filters(network_type='drive'):
    """ Get the filters with which to interrogate the OpenStreetMao API service.

    Parameters
    ----------
    network_type: str, optional, default: 'drive'
        Type of street network to obtain.
    Returns
    -------
    osm_filters: str
        Filters identifying the type of road network to be obtained
    """
    osm_filters = dict()

    osm_filters['drive'] = ('["highway"]["area"!~"yes"]["access"!~"private"]'
                            '["highway"!~"abandoned|bridleway|bus_guideway|construction|corridor|cycleway|'
                            'elevator|escalator|footway|path|pedestrian|planned|platform|proposed|raceway|steps|track"]'
                            '["service"!~"emergency_access|parking|parking_aisle|private"]')

    osm_filters['bicycle'] = ('["highway"]["area"!~"yes"]["access"!~"private"]'
                              '["highway"!~"abandoned|bridleway|footway|bus_guideway|construction|corridor|elevator|'
                              'escalator|planned|platform|proposed|raceway|steps|footway"]'
                              '["service"!~"private"]["bicycle"!~"no"])')

    osm_filters['service'] = ('["highway"]["area"!~"yes"]["access"!~"private"]["highway"!~"abandoned|bridleway|'
                              'construction|corridor|platform|cycleway|elevator|escalator|footway|path|planned|'
                              'proposed|raceway|steps|track"]["service"!~"emergency_access|parking|'
                              'parking_aisle|private"]["psv"!~"no"]["footway"!~"yes"]')

    return osm_filters[network_type]


def osm_download(bbox, network_type='drive', custom_filter=None):
    """ Get the OpenStreetMap response.

    Parameters
    ----------
    bbox: tuple
        bounding box within N, S, E, W coordinates.
    network_type: str, optional, default: 'drive'
        Type of street network to obtain.
    custom_filter: str or None, optional, default: None
        Custom filter to be used instead of the predefined ones to query the Overpass API.
        An example of a custom filter is the following '[highway][!"footway"]'.
        For more information visit https://overpass-turbo.eu and https://taginfo.openstreetmap.org.

    Returns
    -------
    response: json
        Response of the OpenStreetMao API service.
    """
    north, south, west, east = bbox

    if custom_filter is not None:
        osm_filter = custom_filter
    else:
        osm_filter = get_filters(network_type=network_type)

    url_endpoint = 'https://maps.mail.ru/osm/tools/overpass/api/interpreter'

    timeout = 180
    out_resp = 'json'

    overpass_settings = f'[out:{out_resp}][timeout:{timeout}]'

    query_str = f'{overpass_settings};(way{osm_filter}({south}, {west}, {north}, {east});>;);out;'

    response_json = requests.post(url_endpoint, data={'data': query_str})

    size_kb = len(response_json.content) / 1000
    print(f'Downloaded {size_kb:,.2f}kB')

    return response_json.json()
