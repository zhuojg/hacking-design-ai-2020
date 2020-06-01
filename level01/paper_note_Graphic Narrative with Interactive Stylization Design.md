# **Note** for *Graphic Narrative with Interactive Stylization Design*

## Overview

### Goal

To translate videos and images into storyboards that present the scenes within them in a visually pleasing, effective, and interesting manner.

### Pipeline

1. **Input**  
The input can be a video that last few tens of seconds, or any set of images.

2. **Frame Selection**(Image Selection)  
Select images from the input.

3. **Layout**  
Choose layout to hold the selected images.

4. **Framing**  
Crop and zoom the selected images to fit the layout.

5. **Stylization**  
Stylize the resulting frame.

## Important Components

### Image Selection

The key idea is to remove duplicates and near-duplicates.  
First of all, authors use **Perceptual Hashing** to get feature of each image, and calculate Hamming distance as the difference between two images. So, we can find near-duplicates easily.  
Then authors use the **gradient** to find the sharpest image among several near-duplicates as the selected result.  

### Layout

Manually create a set of layouts.  

### Frameing: Cropping and Zoom

Use 2 CNNs, one for detecting faces, another for detecting objects.  
CNNs will return the bounding box, and authors expand it with some rules.

### Stylization

1. Interactive Style Design  
Create a flexible tool that allows anyone to design stylization filters, regardless of technical ability.  
In general, it is a filter-based app that is as simple as Meitu.

2. Filter Blocks  
This is the core of stylization. There are 3 kinds of filtrs: pixel operations, advanced filters and histogram modification filters.  

### Procedural Styles

Authors use the idea of procedural modeling to generate thousands of ideas. They randomly choose some filters and randomly change their parameters. And finally, they use CNN to evaluate the aesthetic quality of an image.

## Inspiration for Our Design Architecture

1. 最后呈现的结果可以是一个可玩性高、易操作的交互式设计程序。
2. 由于算法的局限性，直接生成”最优“结果可能并不能被人接收，需要有可以调整的部分。
3. 生成速度是必须要考虑的，如果一次结果的生成需要花费大量时间，那么这种思路是不适合用于设计的。
