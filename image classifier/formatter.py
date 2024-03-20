from PIL import Image
import os

def make_square_and_resize(img_path, output_path, size=(256, 256)):
    with Image.open(img_path) as img:
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

        # Resize the cropped image to 256x256
        img_resized = img_cropped.resize(size, Image.Resampling.LANCZOS)

        # Save the processed image
        img_resized.save(output_path, "PNG")

def convert_images(source_dir, target_dir):
    try:
        # Loop through all files in the source directory
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(source_dir, filename)
                output_path = os.path.join(target_dir, os.path.splitext(filename)[0] + '.png')
                make_square_and_resize(file_path, output_path)
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    source_dir = 'data/unformatted'  # Where images come from
    target_dir = 'data/formatted'  # Where images get saved to after formatting

    # Create the target directory if it does not exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    convert_images(source_dir, target_dir)