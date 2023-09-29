import typer
import os
import cv2
import napari
import numpy as np
import pyvirtualcam
from magicgui import magic_factory
from napari.qt.threading import thread_worker
import time
import logging
from napari_conference import _widget  # Assuming _widget.py is in the napari_conference package

app = typer.Typer()

@app.command()
def main(filter: str = typer.Option("None", help="Filter to apply. Options are: None, Blur, Laplacian, Gameboy")):
    """
    Run the napari-conference plugin with the specified filter.
    """
    # Set up the filter in the state
    _widget.state.update_mode["filter"] = filter
    
    viewer = napari.Viewer()
    viewer.window.resize(800, 600)

    conference_widget = _widget.conference_widget()
    viewer.window.add_dock_widget(conference_widget, name="Conference")

    napari.run()

if __name__ == "__main__":
    app()
