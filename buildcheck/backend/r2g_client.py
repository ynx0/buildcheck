import requests
from Pillow import Image
from pathlib import Path




# TODO pull this directly from the runpod or better yet use endpoint
R2G_API = 'https://s71nx5jaqrdy09-8080.proxy.runpod.net/'

def _img2b64(img: Image) -> str:
	# https://jdhao.github.io/2020/03/17/base64_opencv_pil_image_conversion/
	img_buf = BytesIO()
	img.save(img_buf, format="PNG")
	im_bytes = img_buf.getvalue()
	im_b64 = base64.b64encode(im_bytes)

	return im_b64


def vectorize(img: Image):
	img_b64 = _img2b64(img)
	res = requests.post(f'{R2G_API}/vectorize', json={"input": im_b64})
	return r.json()


