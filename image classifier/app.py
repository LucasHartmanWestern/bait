from model_generator import predict
from PIL import Image
import io

def make_square_and_resize_bytestream(image_bytestream, size=(230, 230)):
    with Image.open(io.BytesIO(image_bytestream)) as img:
        # Determine the size for cropping
        width, height = img.size
        min_side = min(width, height)

        # Calculate the cropping box to make the image square
        left = (width - min_side) / 2
        top = (height - min_side) / 2
        right = (width + min_side) / 2
        bottom = (height + min_side) / 2

        # Crop to make the image square
        img_cropped = img.crop((left, top, right, bottom))

        # Resize the cropped image to the specified size
        img_resized = img_cropped.resize(size, Image.Resampling.LANCZOS)

        # Save the processed image to a bytestream
        output_bytestream = io.BytesIO()
        img_resized.save(output_bytestream, "PNG")
        return output_bytestream.getvalue()

# Get predictions on bytestream images
def get_prediction(bytestream_image):
    product_label, light_status_label = predict(image_bytestream=make_square_and_resize_bytestream(bytestream_image))

    return (product_label, light_status_label)

# Run this file for an example
if __name__ == '__main__':
    # Example usage

    # Get example image and turn it into a bytestream
    image = Image.open("data/predict_this.png")
    byte_stream = io.BytesIO()
    image.save(byte_stream, format='PNG')
    image_bytes = byte_stream.getvalue()

    # Get prediction
    prediction = get_prediction(image_bytes)

    # Display result
    print(prediction)