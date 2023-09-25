# FirePoint prepares your images for laser engraving

Command line program to convert an image to a more "engraver ready" image.
Default values should provide decent results, many different effects can be achieved my using the numerous parameters.

## Examples

![image](https://raw.githubusercontent.com/fdev31/firedot/main/images/ref.png)

this color image is the input which have been used to generate the following 4x4cm wooden squares from those images:

![image](https://raw.githubusercontent.com/fdev31/firedot/main/images/output.jpg)

![image](https://raw.githubusercontent.com/fdev31/firedot/main/images/img1.png)
![image](https://raw.githubusercontent.com/fdev31/firedot/main/images/img3.png)

*Note*: such output image is too bright / requires high power (not ideal):

![image](https://raw.githubusercontent.com/fdev31/firedot/main/images/img2.png)

## Syntax

```
firepoint [options] <source image> <output image>
```

## Installation

`pip install firedot`


## Options

- `--use_squares` draws squares instead of circles, sometimes provides better results
- `--width` forces a specific width (in pixels) for the output image
- `--multiply` makes the image more dark (<1) or brighter (>1)
- `--normalize` performs a normalization of the colors, `0` to disable up to `1` (100% normalized)
- `--sharpen` sharpens the image, `0` to disable up to `1` (100% sharper)
- `--hypersample` When > 1, will work on a higher definition image and will re-scale it down at the end. Generally increasing the quality drastically, but can lead to weird effects with some values `3` and `5` can provide spectacular results but `1` leads to more consistent output across laser settings (outputs a pure black & white image).

## Advanced options

Check `firepoint --help`

# Typical usage

Check the following apps for a complete engraving ecosystem:

- https://github.com/johannesnoordanus/image2gcode can be used to convert firepoint images to gcode use the `--pixelsize` matching your machine
- https://github.com/johannesnoordanus/grblhud allows sending the gcode & controlling the machine

