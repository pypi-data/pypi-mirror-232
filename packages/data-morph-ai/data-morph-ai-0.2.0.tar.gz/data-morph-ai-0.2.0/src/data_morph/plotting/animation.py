"""Utility functions for animations."""

import glob
from pathlib import Path
from typing import Union

from PIL import Image

from ..shapes.bases.shape import Shape


def stitch_gif_animation(
    output_dir: Union[str, Path],
    start_shape: str,
    target_shape: Union[str, Shape],
    keep_frames: bool = False,
    forward_only_animation: bool = False,
) -> None:
    """
    Stitch frames together into a GIF animation.

    Parameters
    ----------
    output_dir : str or pathlib.Path
        The output directory to save the animation to. Note that the frames to
        stitch together must be in here as well.
    start_shape : str
        The starting shape.
    target_shape : str or Shape
        The target shape for the morphing.
    keep_frames : bool, default ``False``
        Whether to keep the individual frames after creating the animation.
    forward_only_animation : bool, default ``False``
        Whether to only play the animation in the forward direction rather than
        animating in both forward and reverse.

    See Also
    --------
    PIL.Image
        Frames are stitched together with Pillow.
    """
    output_dir = Path(output_dir)

    # find the frames and sort them
    imgs = sorted(glob.glob(str(output_dir / f'{start_shape}-to-{target_shape}*.png')))

    frames = [Image.open(img) for img in imgs]

    if not forward_only_animation:
        # add the animation in reverse
        frames.extend(frames[::-1])

    frames[0].save(
        output_dir / f'{start_shape}_to_{target_shape}.gif',
        format='GIF',
        append_images=frames[1:],
        save_all=True,
        duration=5,
        loop=0,
    )

    if not keep_frames:
        # remove the image files
        for img in imgs:
            Path(img).unlink()
