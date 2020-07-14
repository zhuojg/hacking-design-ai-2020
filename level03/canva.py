import os
import colorgram
from PIL import Image, ImageDraw, ImageFont
from Katna.image import Image as kImage
import cv2
import matplotlib.pyplot as plt
import pyimgsaliency as psal
import random
from deap import base, creator, tools, algorithms
import numpy as np
import array
import colorsys


def get_img_saliency(filename):
    mbd = psal.get_saliency_mbd(filename).astype('uint8')
    binary_sal = psal.binarise_saliency_map(mbd, method='adaptive')

    return mbd, binary_sal


class Slide:
    def __init__(self, content, category, **kwargs):
        self.content = content
        self.category = category
        self.x = 0
        self.y = 0

        if category == 'text':
            self.color = '#000000'
            self.font = ImageFont.truetype(kwargs['font_path'], size=kwargs['font_size'])

            self.size = self.font.getsize(self.content)
        elif category == 'image':
            self.img = Image.open(kwargs['img_path'])
            result_size = kwargs['boundary_size']
            height_ratio = result_size[1] / self.img.size[1]
            width_ratio = result_size[0] / self.img.size[0]

            scale_ratio = min(height_ratio, width_ratio)
            self.img = self.img.resize((int(self.img.size[0] * scale_ratio), int(self.img.size[1] * scale_ratio)))
            self.size = self.img.size
        else:
            raise TypeError('Unknown slide type \'%s\'' % category)


class Poster:
    def __init__(self, bg_file_path, size=[1200, 1800]):
        self.size = size
        self.bg_file_path = bg_file_path
        self.img_module = kImage()

        self.slides = []

        self.canva = None
        self.bg_sal = None

    def add_slide(self, content, category, **kwargs):
        self.slides.append(Slide(content, category, **kwargs))

    def generate_background(self):
        cv_image = cv2.imread(self.bg_file_path)
        saliency, saliency_binary = get_img_saliency(self.bg_file_path)

        # get resize ratio, but do not resize cvimage, because this will affect cropping result
        height = cv_image.shape[0]
        width = cv_image.shape[1]

        height_ratio = self.size[1] / height
        width_ratio = self.size[0] / width
        scale_ratio = max(height_ratio, width_ratio)

        # crop background
        crop_list = self.img_module.crop_image_from_cvimage(
            input_image=cv_image,
            crop_width=self.size[0] / scale_ratio,
            crop_height=self.size[1] / scale_ratio,
            num_of_crops=1)

        crop_rect = crop_list[0]
        x_pos, y_pos, width, height = crop_rect.x, crop_rect.y, crop_rect.w, crop_rect.h
        bg_img, bg_sal = cv_image[y_pos:y_pos + height, x_pos:x_pos + width], saliency_binary[y_pos:y_pos + height, x_pos:x_pos + width]

        bg_img = cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB)
        bg_img = Image.fromarray(bg_img)
        bg_sal = Image.fromarray(bg_sal)

        self.bg_sal = bg_sal.resize((self.size[0], self.size[1]), Image.ANTIALIAS)
        self.canva = bg_img.resize((self.size[0], self.size[1]), Image.ANTIALIAS)

    def generate_layout(self, pop_num=50, iter_num=10):
        # generate layout using generetic algorithm
        creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        # Attribute generator 
        toolbox.register("attr_bool", random.random)

        # Structure initializers
        # the last para is the number of individuals, it is equal to slides number * 2, because every slide have x and y to be determined by algorithm
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 2 * len(self.slides)) 
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def evalOneMax(individual):
            roi_rects = []

            for i, item in enumerate(self.slides):
                # rect -> (x, y, w, h)
                roi_rects.append(
                    (int(individual[i * 2] * self.size[0]), int(individual[i * 2 + 1] * self.size[1]), item.size[0], item.size[1])
                )
            
            bg_sal_copy = self.bg_sal.copy()
            result = np.zeros((self.size[1], self.size[0]), dtype='float')

            for item in roi_rects:
                # if these rects are beyond the canva, the result is bad
                # return 1. directly
                if (item[0] + item[2]) > self.size[0] or (item[1] + item[3]) > self.size[1]:
                    return 1.,
            
                # multiply these rects and corresponding saliency roi
                temp_canva = np.zeros((self.size[1], self.size[0]), dtype='float')
                temp_canva[item[1]:item[1] + item[3], item[0]:item[0] + item[2]] = np.ones((item[3], item[2]), dtype='float')

                # TODO: consider the overlap of each slides
                result += (bg_sal_copy * temp_canva)
            
            # return the average value of each pixel
            return np.mean(result),

        toolbox.register("evaluate", evalOneMax)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        
        def loop():
            pop = toolbox.population(n=pop_num)
            hof = tools.HallOfFame(1)
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", np.mean)
            stats.register("std", np.std)
            stats.register("min", np.min)
            stats.register("max", np.max)

            pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=iter_num, 
                                           stats=stats, halloffame=hof, verbose=True)
            
            return hof[0]
        
        print('Generating layout...')
        positions = loop()
        for i in range(len(self.slides)):
            self.slides[i].x = int(positions[i * 2] * self.size[0])
            self.slides[i].y = int(positions[i * 2 + 1] * self.size[1])

        print('Layout generated.')


    def generate_text_color(self):
        for item in self.slides:
            if item.category == 'text':
                pass

    def render(self):
        self.generate_background()
        self.generate_layout(pop_num=50, iter_num=30)

        draw = ImageDraw.Draw(self.canva)

        for item in self.slides:
            if item.category == 'text':
                item_pos = (item.x, item.y, item.x + item.size[0], item.y + item.size[1])
                draw.text(xy=item_pos, text=item.content, fill=item.color, font=item.font)
            elif item.category == 'image':
                self.canva.paste(item.img, (item.x, item.y, item.x + item.size[0], item.y + item.size[1]))

    def show(self):
        self.canva.show()
        self.bg_sal.show()
