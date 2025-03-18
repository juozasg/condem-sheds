# top-left X = 4249
# top-left Y = 6057

# bottom-right X = 4351
# bottom-right Y = 6135

# width = height =~ 1.85km


import os
import random
import subprocess
from time import sleep

BLOCK_WIDTH = 8
BLOCK_HEIGHT = 8
TILE_START_X = 4249
TILE_START_Y = 6057
# MAX_X = 4351
# MAX_Y = 6135
COUNT_BLOCKS_X = 13
COUNT_BLOCKS_Y = 10

global DL_BLOCKS
DL_BLOCKS = 0
global DL_TILES
DL_TILES = 0

def block_tile_coords_list(block_x, block_y):
	x0 = TILE_START_X + block_x * BLOCK_WIDTH
	y0 = TILE_START_Y + block_y * BLOCK_HEIGHT

	coords_list = []
	for y in range(y0, y0 + BLOCK_HEIGHT):
			for x in range(x0, x0 + BLOCK_WIDTH):
					coords_list.append((x, y))
	return coords_list


def get_path(tile_x, tile_y, block_x, block_y):
	block_x_str = f'{block_x:03d}'
	block_y_str = f'{block_y:03d}'
	return f'tiles/z14/{block_x_str}-{block_y_str}/{tile_x}-{tile_y}.webp'

def download_tile_cmd(tile_x, tile_y, block_x, block_y):
	url = f'https://mapsresources-pa.googleapis.com/v1/tiles?map_id=611c009377cf1375&version=sdk-9050355765241630285&sdk_map_variant=1&pb=!1m5!1m4!1i14!2i{tile_x}!3i{tile_y}!4i256!2m3!1e0!2sm!3i723481389!3m13!2sen-US!3sUS!5e18!12m5!1e68!2m2!1sset!2sRoadmap!4e2!12m3!1e37!2m1!1ssmartmaps!4e0!5m2!1e3!5f2!23i56565656!26m2!1e2!1e3'
	path = get_path(tile_x, tile_y, block_x, block_y)

	block_x_str = f'{block_x:03d}'
	block_y_str = f'{block_y:03d}'
	subprocess.run(["mkdir", "-p", f'tiles/z14/{block_x_str}-{block_y_str}'])

	# url = "https://httpstat.us/403"
	cmd = f"curl '{url}' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0' -H 'Accept: image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'Alt-Used: mapsresources-pa.googleapis.com' -H 'Connection: keep-alive' -H 'Sec-Fetch-Dest: image' -H 'Sec-Fetch-Mode: no-cors' -H 'Sec-Fetch-Site: cross-site' -H 'Priority: u=5' -H 'TE: trailers' --compressed -o {path}"


	# subprocess.run(cmd, shell=True)
	# print(cmd)
	return cmd

	# subprocess.run(["wget", "-O", f"tiles/{tile_x}-{tile_y}.webp", url])


def download_block(block_x, block_y):
	coords_list = block_tile_coords_list(block_x, block_y)
	cmd_list = []
	# for coords in coords_list:
		# cmd_list.append(download_tile_cmd(*coords, block_x, block_y))

	# use Popen to run multiple commands in parallel
	# max 8 parallel downloads
	n = 8
	for i in range(0, len(coords_list), n):
		coords = coords_list[i:i+n]
		cmds = [download_tile_cmd(*coord, block_x, block_y) for coord in coords]
		paths = [get_path(*coord, block_x, block_y) for coord in coords]
		# cmds = cmd_list[i:i+n]
		processes = [subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for cmd in cmds]
		for p in processes:
			p.wait()
		# sleep random 0.5 to 2 seconds
		for path in paths:
			# if file size is 0 or not exist then error
			if not os.path.exists(path) or (os.path.exists(path) and os.path.getsize(path) == 0):
				print(f"!! Error downloading path {path}")
				print("commands:")
				print(cmds)
				exit(1)

		global DL_TILES
		DL_TILES += n
		# print(f"Downloaded {DL_TILES} tiles")
		sleep(0.5 + 1.5 * random.random())



# download_block(0, 0)

# got 0,0 to 3,1

limit_block_x_min = 0
limit_block_x_max = 12
limit_block_y_min = 2
limit_block_y_max = 9



for block_y in range(COUNT_BLOCKS_Y):
	for block_x in range(COUNT_BLOCKS_X):
		if block_x < limit_block_x_min or block_x > limit_block_x_max or block_y < limit_block_y_min or block_y > limit_block_y_max:
			continue
		print(f"Downloading block {block_x}, {block_y}")
		download_block(block_x, block_y)
		print(f"Got block {block_x}, {block_y}")
		print(f"Total tiles: {DL_TILES}")
		DL_BLOCKS += 1
		sleep(10 + 1.5 * random.random())

		if DL_BLOCKS % 10 == 0:
			t = 60 + 600 * random.random()
			print(f"Sleep {t}s")
			sleep(t)



print(f"Downloaded {DL_BLOCKS} blocks")