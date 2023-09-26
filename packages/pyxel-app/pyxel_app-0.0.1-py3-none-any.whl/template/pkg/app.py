import pyxel
from .utils import *

class Params:
    WINDOW_SIZE = (100,100)
    SOURCE = get_data_path("data/img.pyxres")

class App:
    def __init__(self, params:Params) -> None:
        # initialize window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = params.WINDOW_SIZE
        pyxel.init(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # load data
        pyxel.load(params.SOURCE)
        
        # initialize variables
        self._reset(params)
        
        # run app
        pyxel.run(self._update, self._draw)
    
    # initialize variables
    def _reset(self, params:Params):
        self.params = params
    
    # process
    def _update(self):
        pass
    
    # visualize
    def _draw(self):
        pass