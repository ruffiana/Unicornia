import requests
from urllib.parse import urlparse
from pathlib import Path

try:
    from .actions import ActionManager
except ImportError:
    from actions import ActionManager


def save_image_from_url(url: str, path: Path, action_name: str, spoiler: bool = False):
    """
    # Example usage:
    # save_image_from_url("https://example.com/image.jpg", "images", spoiler=True)

    """
    # Ensure the folder exists
    folder_path = path / action_name
    folder_path.mkdir(parents=True, exist_ok=True)

    # Parse the URL and get the original filename
    parsed_url = urlparse(url)
    original_filename = Path(parsed_url.path).name

    # Add "SPOILER_" prefix if the spoiler flag is set
    filename_prefix = "SPOILER_" if spoiler else ""

    # Create the base filename using the folder name and counter
    base_filename = f"{action_name}"

    # Generate the new filename with a two-digit increment counter
    counter = 1
    while True:
        new_filename = f"{filename_prefix}{base_filename}_{counter:02}{Path(original_filename).suffix}"
        file_path = folder_path / new_filename
        if not file_path.exists():
            break
        counter += 1

    # Download the image
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.HTTPError:
        print(f"{action_name} : Error downloading {url}.")
        return

    # Write the image to the specified file path
    file_path.write_bytes(response.content)
    print(f"Image saved to {file_path}")


if __name__ == "__main__":
    from pprint import pprint

    images_path = Path(__file__).parent / "images"

    manager = ActionManager()

    actions = manager.list()
    for action_name in actions:
        action = manager.get(action_name)
        for image_URL in action.images:
            save_image_from_url(image_URL, images_path, action_name, action.spoiler)
