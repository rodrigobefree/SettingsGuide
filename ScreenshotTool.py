# Copyright (C) 2021 Ghostkeeper
# This plug-in is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
# You should have received a copy of the GNU Affero General Public License along with this plug-in. If not, see <https://gnu.org/licenses/>.

import collections
import typing

if typing.TYPE_CHECKING:
	from PyQt5.QtGui import QImage  # Screenshots are returned as QImage by the Snapshot tool of Cura.

"""
This module provides an automatic way to generate screenshots for the Settings Guide.

The goals of this tool are:
* To have a canonical way to create screenshots, ensuring that the look and feel is consistent.
* To be able to re-create screenshots automatically, if Cura changes something in the way that their scene looks.
* To ensure that screenshots are compressed properly.
* To allow external contributors to define screenshots through code.

The process of creating these screenshots is very complex! It involves several stages and has a bunch of
dependencies. The dependencies that need to be installed to create the screenshots are:
* Linux: The tool is only designed to work on Linux at the moment.
* OpenSCAD: After downloading the 3D model files, they are compiled with OpenSCAD to STL files that Cura can read.
* ImageMagick: Used to reduce colour depth and to combine screenshots into GIF animations.
* OptiPNG: To pre-process for optimising PNG files.
* Efficient-Compression-Tool: To refine optimisation of PNG files.
* Gifsicle: To optimise GIF files.

These dependencies can be installed on Ubuntu by running:
`sudo apt install openscad gimp optipng gifsicle`
Only Efficient-Compression-Tool has to be compiled separately from source. Make sure it ends up in the path. It can
be found here: https://github.com/fhanau/Efficient-Compression-Tool

The tool is available by setting the preference "settings_guide/screenshot_tool" to True. A button will then be
visible on every article. When pressed, it will re-create the images for that article. A button will also be present
on the landing page that will re-create ALL images. This takes a long time!
"""

# These are several system commands we can execute to perform various tasks using external tools.
commands = {
	"openscad": "openscad -o {output} {input}",  # Compile an OpenSCAD file.
	"reduce_palette": "convert -colors {colours} {input} png:{output}",  # Reduce colour palette of an image.
	"optimise_png": "optipng -o7 -strip all -snip -out {output} {input} && ect -9 -strip --allfilters-b --pal_sort=120 --mt-deflate {output}",  # Reduce file size of PNG images.
	"merge_gif": "convert -delay {delay} -loop 0 {inputs} {output}",  # Merge multiple images into a GIF.
	"optimise_gif": "gifsicle -O3 {input}"  # Reduce file size of GIF images.
}

ScreenshotInstruction = collections.namedtuple("ScreenshotInstruction", ["image_path", "model_path", "camera_position", "camera_lookat", "layer", "line", "settings", "colours", "width", "height", "delay"])
"""
All the information needed to take a screenshot.
* image_path: The filename of the image to refresh in the articles/images folder.
* model_path: The filename of the 3D model in the models folder.
* camera_position: The X, Y and Z position of the camera (as list).
* camera_lookat: The X, Y and Z position of the camera focus centre.
* layer: The layer number to look at. Use layer -1 to not use layer view. Use a list to define an animation.
* line: The number of lines to show on the current layer. Use 0 to view the entire layer. Use a list to define an
  animation.
* settings: A dictionary of setting keys and values to slice the object with.
* colours: The colour depth of the resulting image. Reduce colours to reduce file size. Max 256.
* width: The width of the resulting screenshot.
* height: The height of the resulting screenshot.
* delay: If this is an animation, the delay between consecutive images in milliseconds.
"""

def refresh_screenshots(article_text) -> None:
	"""
	Refresh the screenshots nested in the selected article text.

	This function serves as glue code and an overview of the stages through which we go in order to refresh the
	screenshots.
	:param article_text: The text containing embedded screenshots to refresh.
	"""
	for screenshot_instruction in find_screenshots(article_text):
		setup_printer(screenshot_instruction.settings)
		stl_path = convert_model(screenshot_instruction.model_path)
		load_model(stl_path)

		if type(screenshot_instruction.layer) != list:  # To simplify processing, always use lists for the layer and line, pretending it's always an animation.
			screenshot_instruction.layer = [screenshot_instruction.layer]
		if type(screenshot_instruction.line) != list:
			screenshot_instruction.line = [screenshot_instruction.line]

		is_animation = len(screenshot_instruction.layer) > 1
		if screenshot_instruction.layer[0] >= 0:
			slice_scene()

		# Track saved images in case we're making multiple that need to be combined into a GIF later.
		saved_images = []
		index = 0
		for layer, line in zip(screenshot_instruction.layer, screenshot_instruction.line):
			if layer >= 0:  # Need to show layer view.
				switch_to_layer_view()
				navigate_layer_view(layer, line)
			else:  # Need to show the model itself.
				switch_to_solid_view()
			screenshot = take_snapshot(screenshot_instruction.camera_position, screenshot_instruction.camera_lookat, screenshot_instruction.width, screenshot_instruction.height)
			if not is_animation:
				target_file = screenshot_instruction.image_path
			else:
				target_file = screenshot_instruction.image_path + str(index) + ".png"
			save_screenshot(screenshot, target_file)
			saved_images.append(target_file)
			index += 1

		if is_animation:
			combine_animation(saved_images, screenshot_instruction.image_path, screenshot_instruction.colours)
			optimise_gif(screenshot_instruction.image_path)
		else:
			reduce_colours(screenshot_instruction.image_path, screenshot_instruction.colours)
			optimise_png(screenshot_instruction.image_path)

def find_screenshots(article_text) -> typing.Generator[ScreenshotInstruction, None, None]:
	"""
	Finds the screenshot instructions and parses them to ScreenshotInstruction instances, so that the rest of the
	module may more easily process them and refresh screenshots.
	:param article_text: The article to find screenshots in, HTML-formatted.
	:return: A sequence of ScreenshotInstruction instances.
	"""
	if False:
		yield None
	return  # TODO

def setup_printer(settings) -> None:
	"""
	Set up a Cura printer and set the settings as desired in the screenshot instruction.

	This makes sure that the model will be sliced with the correct settings.
	:param settings: The settings to slice the model with, as a dictionary of setting keys to setting values.
	"""
	pass  # TODO

def convert_model(scad_path) -> str:
	"""
	Convert an OpenSCAD file into an STL model.

	The STL model will be saved in a temporary file.
	:param scad_path: A path to an OpenSCAD model file.
	:return: A path to an STL model file.
	"""
	return ""  # TODO

def load_model(stl_path) -> None:
	"""
	Load a 3D model into the scene to take a screenshot of.
	:param stl_path: A path to an STL model to load.
	"""
	pass  # TODO

def slice_scene() -> None:
	"""
	Trigger a slice, so that we can show layer view in the screenshot.
	"""
	pass  # TODO

def switch_to_layer_view() -> None:
	"""
	Show layer view in the screenshot.
	"""
	pass  # TODO

def navigate_layer_view(layer_nr, line_nr) -> None:
	"""
	Set the layer slider and line slider to the correct positions for the screenshot.
	:param layer_nr: The layer number to show on the screenshot.
	:param line_nr: The line to show on the screenshot. Use 0 to show the entire layer.
	"""
	pass  # TODO

def switch_to_solid_view() -> None:
	"""
	Show solid view in the screenshot.
	"""
	pass  # TODO

def take_snapshot(camera_position, camera_lookat, width, height) -> "QImage":
	"""
	Take a snapshot of the current scene.
	:param camera_position: The position of the camera to take the snapshot with.
	:param camera_lookat: The position of the focal point of the camera.
	:param width: The width of the snapshot, in pixels.
	:param height: The height of the snapshot, in pixels.
	:return: A screenshot of the current scene.
	"""
	pass  # TODO

def save_screenshot(screenshot, image_path) -> None:
	"""
	Save the screenshot to file in the plug-in folder.
	:param screenshot: The image to save to the file.
	:param image_path: The file path to store the screenshot in.
	"""
	pass  # TODO

def combine_animation(frames, image_path, colours) -> None:
	"""
	Combine the frames of an animation into a GIF file.
	:param frames: A list of PNG files storing the frames of the animation, in order.
	:param image_path: The path to the GIF file to store.
	:param colours: The number of colours to use in the palette of the GIF.
	"""
	pass  # TODO

def optimise_gif(image_path) -> None:
	"""
	Do a compression optimisation on a GIF file.
	:param image_path: A path to the GIF file to optimise.
	"""
	pass  # TODO

def reduce_colours(image_path, colours) -> None:
	"""
	Reduce the colour palette of a PNG image.
	:param image_path: A path to the PNG image to reduce the colour palette of.
	:param colours: The desired number of colours to use in the palette of the PNG file.
	"""
	pass  # TODO

def optimise_png(image_path) -> None:
	"""
	Do a compression optimisation on a PNG file.
	:param image_path: A path to the PNG file to optimise.
	"""
	pass  # TODO