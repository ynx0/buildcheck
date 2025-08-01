import os
import sys
import requests
from PIL import Image
from pathlib import Path
from .blueprints import bp_name2image, bp_name2r2g
from dotenv import load_dotenv
from io import BytesIO
import base64
from json import JSONDecodeError
from .vectorization import Room
from pprint import pprint
import json


DEBUG = True

load_dotenv()

def _get_r2g_url() -> str:
	R2G_PORT=8080
	response = requests.get("https://rest.runpod.io/v1/pods", headers={"Authorization": f"Bearer {os.getenv('RUNPOD_KEY')}"})
	r = response.json()[0]
	return f'https://{r['id']}-{R2G_PORT}.proxy.runpod.net'

R2G_API = _get_r2g_url()


if DEBUG:
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


def unscale_point(x: int, y: int, scale_factor: float):
	# N.B. scale_factor is what was used to shrink coords to 512x512
	#      which is what we get.
	#      i.e. scaled = (x,y) * scale_factor
	#      so we must multiply by scale_factor^-1 to undo it
	#      e.g. unscaled = scaled * scale_factor^-1
	#                    = (x,y) * scale_factor * scale_factor^-1
	#                    = (x,y)
	scale_inv = 1/scale_factor
	return (scale_inv * x, scale_inv * y)

def unscale_room(juncts: list, scale_factor: float) -> list:
	return list(map(lambda p: unscale_point(*p, scale_factor), juncts))

def vectorize(file_name: str, employee_id: int) -> list[Room]:
	r2g_cached = bp_name2r2g(file_name, employee_id)
	payload = None


	if not r2g_cached.exists():
		print(f'no cached result for {employee_id=} {file_name=}')
		print('calling r2g')
		img = bp_name2image(file_name, employee_id)
		img_b64 = _img2b64(img)
		res = requests.post(f'{R2G_API}/vectorize', json={"input": img_b64})

		try:
			payload = res.json()
		except JSONDecodeError as e:
			print(e)
			raise Exception("error calling vectorize. check if runpod container is running")
	else:
		print(f'found cached result for {employee_id=} {file_name=}')
		with open(r2g_cached, 'r', encoding='utf-8') as f:
			payload = json.load(f)

	# TODO we need to experiment and handle what happens when r2g fails
	# right now rooms is just null

	# extract rooms from payload
	rooms_raw = payload["rooms"]
	scale_factor = payload["scale_factor"]

	if rooms_raw and not r2g_cached.exists():
		# if r2g worked fine and we have detected rooms
		# we'll save this json to reuse later
		with open(r2g_cached, 'w', encoding='utf-8') as f:
		    json.dump(payload, f, ensure_ascii=False, indent=4)

		print(f'finished writing to cache {employee_id=} {file_name=}')

	# discard semantic for now, keeping only junction points
	room_polys_raw = list(map(lambda d: d['room_junctions'], rooms_raw))


	# flatten dict to tuples of coords
	flatten_coord = lambda c: (c['x'], c['y'])
	room_polys_flat = [list(map(flatten_coord, room_poly)) for room_poly in room_polys_raw]



	# scale rooms
	room_polys = [unscale_room(room_poly, scale_factor) for room_poly in room_polys_flat]

	# create `Room`s for each polygon-array

	rooms = [Room.from_junctions(room_poly) for room_poly in room_polys]

	if DEBUG:
		# print(f'{scale_factor=} {rooms_raw=}')
		# print()
		# print()

		# print(f'{room_polys_raw=}')
		# print()
		# print()

		# print(f'{room_polys_flat=}')
		# print()
		# print()

		# print(f'{room_polys=}')
		# print()
		# print()


		print(f'{rooms=}')
		print()
		print()


	return rooms


if __name__ == '__main__':
	print('starting')
	vec = vectorize(file_name, employee_id)
	print("vec result")
	pprint(vec)

