# from diffusers import StableDiffusionPipeline
# import torch
# import os

from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import torch
import os

def train_generative_model(data_folder):
    """
    Train a generative AI model using saved frames.
    Placeholder function for actual training logic.
    """
    # Placeholder: Save the model to a file
    model_path = os.path.join(data_folder, 'generative_model')
    os.makedirs(model_path, exist_ok=True)

    # For now, just return the model path
    return model_path

from diffusers import StableDiffusionPipeline
import torch
import os

# def generate_synthetic_image(prompt, model_name='stabilityai/stable-diffusion-2'):
#     """
#     Generate a synthetic image using a generative AI model.
#     """
#     try:
#         # Check if a GPU is available
#         device = "cuda" if torch.cuda.is_available() else "cpu"
#         torch_dtype = torch.float16 if device == "cuda" else torch.float32

#         # Load the Stable Diffusion pipeline
#         pipe = StableDiffusionPipeline.from_pretrained(model_name, torch_dtype=torch_dtype)
#         pipe = pipe.to(device)

#         # Generate the synthetic image
#         image = pipe(prompt).images[0]

#         # Save the generated image
#         output_path = os.path.join('generative_ai_data', 'synthetic_image.png')
#         image.save(output_path)

#         return output_path
#     except Exception as e:
#         raise ValueError(f"Error generating synthetic image: {str(e)}")
    


def generate_synthetic_image_with_ip(prompt, input_image_path, model_name='stabilityai/stable-diffusion-2'):
    """
    Generate a synthetic image using a generative AI model based on a text prompt and an input image.

    Args:
        prompt (str): The text prompt for generating the image.
        input_image_path (str): The path to the input image.
        model_name (str): The name of the generative AI model to use.

    Returns:
        str: The path to the generated synthetic image.
    """
    try:
        # Check if a GPU is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        # Load the Stable Diffusion Image-to-Image pipeline
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_name, torch_dtype=torch_dtype)
        pipe = pipe.to(device)

        # Load the input image
        input_image = Image.open(input_image_path).convert("RGB")

        # Generate the synthetic image
        image = pipe(prompt=prompt, image=input_image, strength=0.75, guidance_scale=7.5).images[0]

        # Save the generated image
        output_path = os.path.join('generative_ai_data', 'synthetic_image_ip.png')
        image.save(output_path)

        return output_path
    except Exception as e:
        raise ValueError(f"Error generating synthetic image: {str(e)}")