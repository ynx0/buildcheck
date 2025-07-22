from pathlib import Path
from Pillow import Image
import reflex as rx

BLUEPRINT_HOME = Path('./uploaded_files')




def bp_name2path(file_name: str, employee_id: int):
    user_dir = rx.get_upload_dir() / ('user_' + str(uid))
    user_dir.mkdir(parents=True, exist_ok=True)

    return user_dir / file_name


def bp_name2image(file_name: str, employee_id: int) -> Image:
	return Image.open(bp_name2path(file_name, employee_id))



