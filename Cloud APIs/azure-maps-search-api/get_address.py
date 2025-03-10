import os
from dataclasses import dataclass

import click
from PIL import Image, ExifTags
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Stores the Azure Maps subscription key into a variable for later use
subscription_key = os.environ['AZURE_MAPS_KEY']


@dataclass
class GPSCoordinate:
    """
    Represents a GPS coordinate in degrees, minutes, seconds, and direction format.

    This class encapsulates the representation of a geographical coordinate using
    its degrees, minutes, seconds, and cardinal direction. It provides a method
    to convert the coordinate into its decimal format for easier computation or
    representation.

    :ivar degrees: The degree component of the GPS coordinate.
    :type degrees: float
    :ivar minutes: The minute component of the GPS coordinate.
    :type minutes: float
    :ivar seconds: The second component of the GPS coordinate.
    :type seconds: float
    :ivar direction: The cardinal direction of the GPS coordinate ('N', 'S', 'E', 'W').
    :type direction: str
    """
    degrees: float
    minutes: float
    seconds: float
    direction: str

    def __repr__(self):
        return f"{self.degrees}° {self.minutes}' {self.seconds}\" {self.direction}"

    def __str__(self):
        return f"{self.degrees}° {self.minutes}' {self.seconds}\" {self.direction}"

    def to_decimal(self):
        """
        Converts the GPS coordinate into its decimal format.
        :return: The decimal representation of the GPS coordinate.
        """
        return float(self.degrees + self.minutes / 60 + self.seconds / 3600) * (
            -1 if self.direction in ['S', 'W'] else 1)


@dataclass
class GPSLocation:
    """
    Represents a geographical location specified by latitude and longitude.

    This class is used to store and manage latitude and longitude
    coordinates encapsulated by the GPSCoordinate type.

    :ivar latitude: Represents the latitude of the location.
    :type latitude: GPSCoordinate
    :ivar longitude: Represents the longitude of the location.
    :type longitude: GPSCoordinate
    """
    latitude: GPSCoordinate
    longitude: GPSCoordinate


def _get_gps_location(img: Image.Image) -> GPSLocation | None:
    """
    Extracts the GPS location from the EXIF data of an image.
    :param img: The image to extract the GPS location from.
    :return: A GPSLocation object containing the latitude and longitude of the image; None if no GPS data is found.
    """

    # Check if the image has EXIF data
    exif_data = img.getexif()
    if exif_data is None:
        return None

    # Extract the GPS information from the EXIF data
    gps_info = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
    if gps_info is None:
        return None

    lat = gps_info.get(ExifTags.GPS.GPSLatitude)            # (degrees, minutes, seconds)
    lat_ref = gps_info.get(ExifTags.GPS.GPSLatitudeRef)     # N or S
    lon = gps_info.get(ExifTags.GPS.GPSLongitude)           # (degrees, minutes, seconds)
    lon_ref = gps_info.get(ExifTags.GPS.GPSLongitudeRef)    # E or W

    # If any of the GPS data is missing, return None
    if None in (lat, lon, lat_ref, lon_ref):
        return None

    longitude = GPSCoordinate(lon[0], lon[1], lon[2], lon_ref)
    latitude = GPSCoordinate(lat[0], lat[1], lat[2], lat_ref)

    return GPSLocation(latitude, longitude)


def _search_address(location: GPSLocation) -> str | None:
    """
    Searches for the address of a given GPS location using Azure Maps.
    :param location: The GPS location to search for.
    :return: The formatted address of the location; None if no address is found.
    """

    # Creates a MapsSearchClient instance using the Azure Maps subscription key.
    maps_search_client = MapsSearchClient(AzureKeyCredential(subscription_key))

    # Performs reverse geocoding to retrieve the address of the given GPS location.
    result = maps_search_client.get_reverse_geocoding(
        coordinates=[location.longitude.to_decimal(), location.latitude.to_decimal()])

    # If there are no location features in the result, return None.
    if 'features' not in result:
        return None

    # If the address property is not found in the location properties, return None.
    props = result['features'][0].get('properties', {})
    if 'address' not in props:
        return None

    # Return the formatted address of the location, or None if not found.
    return props['address'].get('formattedAddress', None)


@click.command()
@click.argument('img_path', type=click.Path(exists=True))
def get_address(img_path: str):
    """
    Processes an image to extract GPS coordinates and retrieve the corresponding
    physical address if available. The function reads an image file, extracts its
    GPS metadata (if present), and retrieves the geographic address corresponding
    to the extracted latitude and longitude. It displays information in the
    console, including the coordinates and the resulting address.

    :param img_path: A file path to the image that contains GPS metadata. The file
        must exist and be a valid image format.
    :type img_path: str

    :return: None
    """

    image = Image.open(img_path)
    location = _get_gps_location(image)

    if location is None:
        print("No se encontraron datos GPS en la imagen.")
        return

    print("Coordenadas GPS encontradas:")
    print(f"Latitud: {location.latitude}")
    print(f"Longitud: {location.longitude}")

    print("\nBuscando dirección...")
    address = _search_address(location)
    if address is None:
        print("No se pudo encontrar la dirección para estas coordenadas.")
        return

    print("Dirección encontrada:")
    print(address)


if __name__ == '__main__':
    get_address()
