import os
import random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance


def add_noise(image):
    # Convert image to array
    image_array = np.array(image)

    # Randomly choose a noise type with reduced intensity
    noise_type = random.choice(['gaussian', 'salt_pepper'])

    if noise_type == 'gaussian':
        mean = 0
        var = random.uniform(0.0005, 0.005)  # Reduced variance
        sigma = var ** 0.5
        gaussian = np.random.normal(mean, sigma, image_array.shape)
        noisy_image = image_array + gaussian
    elif noise_type == 'salt_pepper':
        s_vs_p = 0.5
        amount = random.uniform(0.002, 0.01)  # Reduced amount
        out = np.copy(image_array)
        # Salt mode
        num_salt = np.ceil(amount * image_array.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image_array.shape]
        out[coords] = 255
        # Pepper mode
        num_pepper = np.ceil(amount * image_array.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image_array.shape]
        out[coords] = 0
        noisy_image = out

    # Convert back to image and ensure values are in the valid range
    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_image)


def augment_images(augmented_dir, rotations, flips, num_augmented_per_image):
    for filename in os.listdir('data/formatted'):
        if filename.endswith('.png'):
            image_path = os.path.join('data/formatted', filename)
            image = Image.open(image_path)

            # Convert the image to RGB mode if it's not already in that mode
            if image.mode != 'RGB':
                image = image.convert('RGB')

            for i in range(num_augmented_per_image):
                # Apply a random rotation
                rotation = random.choice(rotations)
                augmented_image = image.rotate(rotation)

                # Apply a random flip
                flip = random.choice(flips)
                if flip == 'horizontal':
                    augmented_image = augmented_image.transpose(Image.FLIP_LEFT_RIGHT)
                elif flip == 'vertical':
                    augmented_image = augmented_image.transpose(Image.FLIP_TOP_BOTTOM)

                # Apply a random crop (crop a random 90% of the original size)
                width, height = augmented_image.size
                new_width, new_height = int(width * 0.9), int(height * 0.9)
                left = random.randint(0, width - new_width)
                top = random.randint(0, height - new_height)
                augmented_image = augmented_image.crop((left, top, left + new_width, top + new_height))

                # Apply random blurring with reduced probability and intensity
                if random.random() < 0.3:  # 30% chance
                    blur_radius = random.uniform(0.2, 1)  # Reduced blur radius
                    augmented_image = augmented_image.filter(ImageFilter.GaussianBlur(blur_radius))

                # Add noise with reduced probability
                if random.random() < 0.3:  # 30% chance
                    augmented_image = add_noise(augmented_image)

                # Save the augmented image
                augmented_filename = f'{filename[:-4]}_aug{i + 1}.png'
                augmented_image.save(os.path.join(augmented_dir, augmented_filename))


if __name__ == '__main__':
    augmented_dir = 'data/augmented'
    os.makedirs(augmented_dir, exist_ok=True)
    rotations = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270]
    flips = [None, 'horizontal', 'vertical']
    num_augmented_per_image = 100

    try:
        augment_images(augmented_dir, rotations, flips, num_augmented_per_image)
        print('Augmentation complete. Augmented images saved in', augmented_dir)
    except Exception as e:
        print(f'Error: {str(e)}')