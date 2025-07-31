from pathlib import Path
from PIL import Image
import reflex as rx

BLUEPRINT_HOME = Path('./uploaded_files')




def bp_user_dir(employee_id: int) -> Path:
    user_dir = rx.get_upload_dir() / ('user_' + str(employee_id))
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def bp_name2path(file_name: str, employee_id: int) -> Path:
    return bp_user_dir(employee_id) / file_name

def bp_name2vispath(file_name: str, employee_id: int) -> Path:
    image_path = bp_name2path(file_name, employee_id)
    output_path = image_path.with_name(image_path.stem + "_output.png")
    return output_path


def bp_name2r2g(file_name: str, employee_id: int) -> Path:
    image_path = bp_name2path(file_name, employee_id)
    output_path = image_path.with_name(image_path.stem + "_r2g.json")
    return output_path



def bp_name2image(file_name: str, employee_id: int) -> Image:
	return Image.open(bp_name2path(file_name, employee_id))



