from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import codecs
import logging

def _start_end_marker_coords_from_point(lat, long):
    import math

    KM_PER_DEGREE = 10000 / 90
    CIRCLE_RADIUS_IN_METERS = 100
    RADIUS_Y = CIRCLE_RADIUS_IN_METERS / 1000 / KM_PER_DEGREE
    RADIUS_X = RADIUS_Y * math.cos(42 / (180 / math.pi))

    POLY_SEGS = 9
    coords = ""
    for r in range(POLY_SEGS + 1):
        rads = r / POLY_SEGS * 2 * math.pi
        coords += "{0},{1} ".format(long + RADIUS_X * math.cos(rads), lat + RADIUS_Y * math.sin(rads))

    return coords

def _placemark_from_trip_and_track(trip_info):
    coords = ""
    for p in trip_info.track:
        coords += "{0},{1} ".format(p.longitude, p.latitude)

    start_coords = ""
    end_coords = ""

    if len(trip_info.track) > 0:
        start_coords = _start_end_marker_coords_from_point(trip_info.track[0].latitude, trip_info.track[0].longitude)
        end_coords = _start_end_marker_coords_from_point(trip_info.track[-1].latitude, trip_info.track[-1].longitude)

    return [
        KML.Placemark(
            KML.name(trip_info.id),
            KML.styleUrl("#hikeTrack"),

            KML.LineString(
                KML.altitudeMode("clampToGround"),

                KML.coordinates(coords)
            )
        ),

        KML.Placemark(
            KML.name(trip_info.id + "-start"),
            KML.styleUrl("#hikeStart"),

            KML.LineString(
                KML.altitudeMode("clampToGround"),

                KML.coordinates(start_coords)
            )
        ),

        KML.Placemark(
            KML.name(trip_info.id + "-end"),
            KML.styleUrl("#hikeEnd"),

            KML.LineString(
                KML.altitudeMode("clampToGround"),

                KML.coordinates(end_coords)
            )
        )
    ]

        # KML.Polygon(
        #     KML.outerBoundaryIs(
        #         KML.LinearRing(
        #             KML.coordinates(start_coords)
        #         )
        #     )
        # ),
        #
        # KML.Polygon(
        #     KML.outerBoundaryIs(
        #         KML.LinearRing(
        #             KML.coordinates(end_coords)
        #         )
        #     )
        # )

# < Polygon > < outerBoundaryIs > < LinearRing >
# < coordinates >
# 135.2, 35.4, 0.
# 135.4, 35.6, 0.
# 135.2, 35.6, 0.
# 135.2, 35.4, 0.
# < / coordinates >
# < / LinearRing > < / outerBoundaryIs > < / Polygon >


def visualize_trips(trips, kml_file):
    """Writes KML for the given trips to the given kml_file path."""

    kml_doc = KML.Document(
        KML.description("Hello, world."),
        KML.Style(
            KML.LineStyle(
                KML.color("1fffffff"),
                KML.width("3")
            ),
            id="hikeTrack"
        ),
        KML.Style(
            KML.LineStyle(
                KML.color("7f00ff00"),
                KML.width("10")
            ),
            id="hikeStart"
        ),
        KML.Style(
            KML.LineStyle(
                KML.color("7f0000ff"),
                KML.width("10")
            ),
            id="hikeEnd"
        )
    )

    for trip in trips:
        kml_doc.extend(
            _placemark_from_trip_and_track(trip)
        )

    with codecs.open(kml_file, 'w', 'utf-8') as file:
        file.write(etree.tostring(KML.kml(kml_doc), encoding='unicode'))

    logging.info("Wrote KML for {0} tracks to '{1}'".format(len(trips), kml_file))
