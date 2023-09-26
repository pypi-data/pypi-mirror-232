import os
import shutil

from .Layer import Layer

class Plotter:
    def add_layer(self, name: str):
        self._layers[name] = Layer(self)

    def update_layer(self, name: str) -> Layer:
        return self._layers[name]
