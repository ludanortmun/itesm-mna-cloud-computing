import io
import os

import click
from PIL import Image, ImageDraw
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Loads the environment variables from the .env file
load_dotenv()

# Get the endpoint and key from the environment variables
endpoint = os.environ["AZURE_FACE_ENDPOINT"]
key = os.environ["AZURE_FACE_API_KEY"]


def _detect_faces(image_content):
    """
    Detects faces in an image using Azure Face API.
    :param image_content: Binary content of the image.
    :return: A set of coordinates for each of the faces in the image.
    """

    # Create a FaceClient with the endpoint and key.
    # Because we are using with, the client will be automatically closed after this code block.
    with FaceClient(endpoint, AzureKeyCredential(key)) as face_client:
        # Calls the detect method with the image content.
        result = face_client.detect(
            image_content,
            detection_model=FaceDetectionModel.DETECTION03,  # The latest detection model.
            recognition_model=FaceRecognitionModel.RECOGNITION04,  # The latest recognition model.
            return_face_id=False,
            return_face_landmarks=False,
        )

    # Azure Face API returns the face rectangles in the format (left, top, width, height).
    # However, to draw the rectangles on top of the image we want the format (left, top, right, bottom).
    return [_to_coords(face.face_rectangle) for face in result]


def _to_coords(face_rectangle):
    """
    Converts the face rectangle to the format expected by PIL.ImageDraw.rectangle.
    :param face_rectangle: A FaceRectangle object returned by Azure Face API.
    :return: A tuple of (left, top, right, bottom).
    """

    return (
        face_rectangle.left,
        face_rectangle.top,
        face_rectangle.left + face_rectangle.width,
        face_rectangle.top + face_rectangle.height,
    )


@click.command()
@click.argument("image_path", type=click.Path(exists=True))
def main(image_path):
    # Reads the contents of the image as binary.
    with open(image_path, "rb") as image_file:
        image_content = image_file.read()

    # Detects faces in the image using Azure Face API.
    detected_faces = _detect_faces(image_content)
    print(f"Found {len(detected_faces)} face(s) in the image.")

    # Converts the image data into an Image object so we can draw rectangles on top of it.
    # To avoid loading the image file again, we can reuse the data from the image_content variable.
    image = Image.open(io.BytesIO(image_content))
    draw = ImageDraw.Draw(image)

    # Draws a green rectangle around each of the detected faces.
    for face in detected_faces:
        draw.rectangle(face, outline="green", width=5)

    # Shows the image with the rectangles around the faces.
    image.show()


if __name__ == "__main__":
    main()
