import cv2
from os import path

template_dir = '/home/dmaczka/ENGE/workspace/contraption maker/templates'
play_states = [ 'nohover', 'hover', 'play_hover', 'play_nohover' ]
playTemplates = dict([ (state, cv2.imread(path.join(template_dir, 'template_{0}.png'.format(state)))) for state in play_states ])
