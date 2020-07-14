# # some input and pre-defined parameters

# title = 'Design AI'
# desc = 'Hacking-Design-AI 2020 in Tongji Design AI Lab.'

# logo_path = './data/logo.jpeg'
# # main_image_path = './data/style.jpg'
# main_image_path = './data/main_image_4.jpg'

from canva import Slide, Poster

p = Poster(bg_file_path='./data/main_image.jpg')
p.add_slide(content='Design AI Lab', category='text', font_size=128, font_path='C:\\Users\\jing\\AppData\\Local\\Microsoft\\Windows\\Fonts\\FZDBSJW.TTF')
p.add_slide(content='Design Hakcing AI', category='text', font_size=64, font_path='C:\\Users\\jing\\AppData\\Local\\Microsoft\\Windows\\Fonts\\FZDBSJW.TTF')
p.add_slide(content='', category='image', img_path='./data/logo.jpeg', boundary_size=(250, 400))

p.render()
p.show()
