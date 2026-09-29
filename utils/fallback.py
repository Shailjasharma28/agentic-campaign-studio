from PIL import Image, ImageDraw

def create_placeholder_image(output_path:str)-> str:

    """
    Create a local placeholder image when primary image generation fails.
    """
    image = Image.new(
        "RGB",
        (1024, 1024),
        "white"
    )

    draw = ImageDraw.Draw(image)

    message = (
        "Image generation\n"
        "temporarily unavailable"

    )

    draw.multiline_text(
        (512, 512),
        message,
        anchor="mm",
        align="center",
        spacing=10
    )

    image.save(output_path)

    return output_path