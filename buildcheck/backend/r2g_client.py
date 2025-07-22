import os
import sys
import requests
from PIL import Image
from pathlib import Path
from .blueprints import bp_name2image
from dotenv import load_dotenv
from io import BytesIO
import base64

load_dotenv()

def _get_r2g_url() -> str:
	R2G_PORT=8080
	response = requests.get("https://rest.runpod.io/v1/pods", headers={"Authorization": f"Bearer {os.getenv('RUNPOD_KEY')}"})
	r = response.json()[0]
	return f'https://{r['id']}-{R2G_PORT}.proxy.runpod.net'

R2G_API = _get_r2g_url()

print(f'R2G_API is {R2G_API}')




# TODO need to pull this directly from the runpod or better yet use endpoint
#      right now, this changes every time we destroy the pod which is somewhat often
# R2G_API = 'https://s71nx5jaqrdy09-8080.proxy.runpod.net'

def _img2b64(img: Image) -> str:
	# https://jdhao.github.io/2020/03/17/base64_opencv_pil_image_conversion/
	img_buf = BytesIO()
	img.save(img_buf, format="PNG")
	img_bytes = img_buf.getvalue()
	img_b64 = base64.b64encode(img_bytes).decode('utf-8')

	return img_b64


def vectorize(img: Image):
	img_b64 = _img2b64(img)
	res = requests.post(f'{R2G_API}/vectorize', json={"input": img_b64})
	return res.json()


if __name__ == '__main__':
	img = bp_name2image('2d-floor-plan.jpg', '2')
	vec = vectorize(img)
	print("vec result")
	print(vec)

