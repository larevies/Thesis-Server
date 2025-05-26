import os
from PIL import Image

source_dir = 'train_cats'
output_dir = 'cats_1861_224'
os.makedirs(output_dir, exist_ok=True)

image_size = (224, 224)
class_names = sorted(os.listdir(source_dir))

print("Preprocessing images.")
counter = 0
for class_name in class_names:
    class_dir = os.path.join(source_dir, class_name)

    if os.path.isdir(class_dir):
        image_files = [f for f in os.listdir(class_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

        for image_file in image_files:
            image_path = os.path.join(class_dir, image_file)
            image = Image.open(image_path)
            original_width, original_height = image.size

            if original_height < original_width:
                scale_factor = image_size[0] / original_height
            else:
                scale_factor = image_size[1] / original_width

            new_height = int(original_height * scale_factor)
            new_width = int(original_width * scale_factor)

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if new_width > image_size[0]:
                left = (new_width - image_size[0]) // 2
                right = left + image_size[0]
                image = image.crop((left, 0, right, new_height))

            if new_height > image_size[1]:
                top = (new_height - image_size[1]) // 2
                bottom = top + image_size[1]
                image = image.crop((0, top, new_width, bottom))

            new_width, new_height = image.size
            if new_height < 224 or new_width < 224:
                continue
            save_dir = os.path.join(output_dir, class_name)
            os.makedirs(save_dir, exist_ok=True)
            image.save(os.path.join(save_dir, f"{counter}.jpg"))
            counter += 1

print(f"Saved {counter} preprocessed images to {output_dir}")
