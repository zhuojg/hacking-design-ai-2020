# to import local lib - pyimgsaliency
# you need to change the path according to your environment
import os

if __name__ == '__main__' and __package__ is None:
    from sys import path
    from os.path import dirname as dir

    path.append(dir(path[0]))
    path.append(os.path.join(dir(path[0]), 'external_lib'))
    __package__ = 'final'

from final.canva import Poster

p = Poster(bg_file_path='../data/image_4_4.jpg', metrics=['saliency', 'overlap'])
p.add_slide(content='夏日特饮', category='text', font_size=128, font_path='../data/FZDBSJW.TTF')
p.add_slide(content='大促期间，第二杯半价', category='text', font_size=64, font_path='../data/FZDBSJW.TTF')
p.add_slide(content='', category='image', img_path='../data/logo.png', boundary_size=(250, 400))

p.render(pop_num=100, iter_num=10)
p.show()
