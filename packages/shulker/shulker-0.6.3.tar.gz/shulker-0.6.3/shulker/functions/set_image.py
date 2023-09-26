import json
import math
import os
import random
import sys
from io import BytesIO
from typing import Union

import PIL
import requests
import urllib3
from PIL import Image

from shulker.components.BlockCoordinates import BlockCoordinates
from shulker.components.BlockHandler import BlockHandler
from shulker.components.BlockZone import BlockZone
from shulker.functions.base_functions import *
from shulker.functions.color_picker import block_from_rgb
from shulker.functions.default import meta_set_block, set_block

# TODO: Minecart method? -> https://www.youtube.com/watch?v=MEawKJm-t28


def generate_instructions_random(pixels, coords, orientation, display_mode="vertical"):
    instructions = generate_instructions(pixels, coords, orientation, display_mode)
    random.shuffle(instructions["cmds"])
    return instructions


def generate_instructions(pixels, coords, orientation, display_mode="vertical"):
    instructions = {"cmds": [], "zone": None}

    x = 0

    for line in pixels:
        x += 1
        z = 0
        for pixel in line:
            block = block_from_rgb(pixel)
            if display_mode == "vertical":
                new_coords = BlockCoordinates(coords.x, coords.y + x, coords.z + z)
            else:
                new_coords = BlockCoordinates(coords.x + x, coords.y, coords.z + z)

            if orientation in block:
                block = block.replace(f"_{orientation}", "")

                if orientation == "side":
                    block.blockhandler.axis = "x"

                elif orientation == "top":
                    block.blockhandler.axis = "x"

            cmd = meta_set_block(
                new_coords,
                block,
                BlockHandler("replace"),
            )
            instructions["cmds"].append(cmd)
            z += 1
    else:
        instructions["zone"] = BlockZone(
            coords, BlockCoordinates(coords.x + x, coords.y, coords.z + z)
        )

    return instructions


def generate_instructions_spiral(pixels, coords, orientation, display_mode="vertical"):
    # TODO only handles vertical for now
    def add_instruction(x, y):
        block = block_from_rgb(pixels[x][y])
        if display_mode == "horizontal":
            relative_cursor = BlockCoordinates(
                coords.x + cursor[0], coords.y, coords.z + cursor[1]
            )
        elif display_mode == "vertical":
            relative_cursor = BlockCoordinates(
                coords.x + cursor[0], coords.y + cursor[1], coords.z
            )

        cmd = meta_set_block(
            relative_cursor,
            block,
            BlockHandler("replace"),
        )
        instructions["cmds"].append(cmd)

    instructions = {"cmds": [], "zone": None}

    width = len(pixels[0])
    height = len(pixels)

    x_center = int(width / 2)
    y_center = int(height / 2)

    cursor = (x_center, y_center)
    add_instruction(cursor[0], cursor[1])

    side = 1
    mult = -1
    while len(instructions["cmds"]) < (width * height - side):
        for _ in range(1, side + 1):
            cursor = (cursor[0] + 1 * mult, cursor[1])
            add_instruction(cursor[0], cursor[1])

        for _ in range(1, side + 1):
            cursor = (cursor[0], cursor[1] + 1 * mult)
            add_instruction(cursor[0], cursor[1])

        mult = mult * -1
        side += 1

    else:
        for _ in range(1, side):
            cursor = (cursor[0] + 1 * mult, cursor[1])
            add_instruction(cursor[0], cursor[1])
        instructions["zone"] = BlockZone(
            coords, BlockCoordinates(coords.x + width, coords.y, coords.z + height)
        )

    return instructions


def generate_instructions_reverse_spiral(
    pixels, coords, orientation, display_mode="vertical"
):
    instructions = generate_instructions_spiral(
        pixels, coords, orientation, display_mode
    )
    instructions["cmds"] = instructions["cmds"][::-1]
    return instructions


def meta_set_image(
    image: Image,
    coords: BlockCoordinates,
    orientation: str,
    display_mode: str = "vertical",
    display_order="normal",
) -> dict:
    pixels = list(image.getdata())

    width, height = image.size
    pixels = [pixels[i * width : (i + 1) * width] for i in range(height)]

    if display_order == "normal":
        instructions = generate_instructions(pixels, coords, orientation, display_mode)
    elif display_order == "random":
        instructions = generate_instructions_random(
            pixels, coords, orientation, display_mode
        )
    elif display_order == "spiral":
        instructions = generate_instructions_spiral(
            pixels, coords, orientation, display_mode
        )
    elif display_order == "reverse_spiral":
        instructions = generate_instructions_reverse_spiral(
            pixels, coords, orientation, display_mode
        )
    else:
        instructions = {"cmds": [], "zone": None}
    return instructions


def set_image(
    source: str,
    coords: Union[BlockCoordinates, tuple],
    orientation: str = "side",
    url: bool = False,
    resize=None,
    display_mode: str = "vertical",
    display_order: str = "normal",
) -> BlockZone:
    """
    This function takes the path to an image or an URL
    (in which case, url must be passed as True), downloads it,
    and sends back the setblocks instruction to print the image
    in the provided orientation

    Orientation can either be "side", "top", "bottom" depending from where
    you want people to look at the image.

    If a player name is provided, the player will be teleported to make sure the
    printing doesn't happen out of bound (and therefore fail)
    """

    check_output_channel()

    if url == True:
        response = requests.get(source)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(source)

    if resize:
        image = image.convert("RGB").resize(resize)

    image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
    if display_mode == "vertical":
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    if display_order == "spiral" or display_order == "reverse_spiral":
        image = image.rotate(90)

    coords = format_arg(coords, BlockCoordinates)

    if orientation not in ["side", "top", "bottom"]:
        raise ValueError(
            f"Orientation must either be side, top or bottom for set_image()"
        )

    instructions = meta_set_image(
        image, coords, orientation, display_mode, display_order
    )
    status = {"cmd": [], "zone": instructions["zone"]}

    for cmd in instructions["cmds"]:
        ret = post(cmd)
        if ret and ret != "":
            status["cmd"].append(ret)

    return True
