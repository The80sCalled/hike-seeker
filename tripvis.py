from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import codecs
import logging


def _placemark_from_trip_and_track(trip_info):
    coords = ""
    for p in trip_info.track:
        coords += "{0},{1} ".format(p.longitude, p.latitude)

    return KML.Placemark(
        KML.name(trip_info.id),
        KML.styleUrl("#hikeTrack"),

        KML.LineString(
            KML.altitudeMode("clampToGround"),

            KML.coordinates(coords)
        )
    )


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
        )
    )

    skip = {"748475"}

    trips = [t for t in trips if t.id not in skip]
    for trip in trips:
        kml_doc.append(
            _placemark_from_trip_and_track(trip)
        )

    with codecs.open(kml_file, 'w', 'utf-8') as file:
        file.write(etree.tostring(KML.kml(kml_doc), encoding='unicode'))

    logging.info("Wrote KML for {0} tracks to '{1}'".format(len(trips), kml_file))
