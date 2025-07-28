import os
import sys
import requests
from PIL import Image
from pathlib import Path
from .blueprints import bp_name2image
from dotenv import load_dotenv
from io import BytesIO
import base64
from json import JSONDecodeError

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


def unscale_point(x: int, y: int, scaling_factor: float):
	# N.B. scaling_factor is what was used to shrink coords to 512x512
	#      which is what we get.
	#      i.e. scaled = (x,y) * scaling_factor
	#      so we must multiply by scaling_factor^-1 to undo it
	#      e.g. unscaled = scaled * scaling_factor^-1
	#                    = (x,y) * scaling_factor * scaling_factor^-1
	#                    = (x,y)
	scale_inv = 1/scaling_factor
	return (scale_inv * x, scale_inv * y)

def unscale_room(juncts: list) -> list:
	return list(map(lambda p: unscale_point(p), juncts))

def vectorize(img: Image) -> list[Room]:
	img_b64 = _img2b64(img)
	res = requests.post(f'{R2G_API}/vectorize', json={"input": img_b64})

	try:
		payload = res.json()
	except JSONDecodeError as e:
		print("error calling vectorize")
		print('check if runpod container is running')
		print(e)


	# extract rooms from payload
	rooms_raw = payload["rooms"]
	scaling_factor = payload["scaling_factor"]

	print(f'{scaling_factor=} {rooms_raw=}')
	print()
	print()

	# discard semantic for now, keeping only junction points
	room_jcts_raw = list(map(lambda d: d['room_junctions'], rooms_raw))

	print(f'{room_jcts_raw=}')
	print()
	print()

	# scale rooms
	room_jcts = [unscale_room(room) for room in room_jcts_raw]

	print(f'{room_jcts=}')
	print()
	print()

	# create `Room`s for each polygon-array

	rooms = [Room.from_junctions(room) for room_jct in room_jcts]
	print(f'{rooms=}')
	print()
	print()


	return rooms





if __name__ == '__main__':
	img = bp_name2image('2d-floor-plan.jpg', '2')
	vec = vectorize(img)
	print("vec result")
	print(vec)

