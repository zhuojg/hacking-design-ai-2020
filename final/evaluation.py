import numpy as np


class Evaluation:
    def __init__(self, bg_sal, rois, metrics=[]):
        self.metrics = metrics
        self.rois = rois
        self.bg_sal = bg_sal
        self.size = bg_sal.size

    def calculate_result(self):
        result = []
        for metric in self.metrics:
            try:
                result.append(eval('self.eval_%s' % metric)())
            except Exception as e:
                print('Unknown metric: %s' % metric)
                print(e)
        
        return tuple(result)

    def eval_saliency(self):
        bg_sal_copy = self.bg_sal.copy()
        result = np.zeros((self.size[1], self.size[0]), dtype='float')

        for item in self.rois:
            # if these rects are beyond the canva, the result is bad
            # return 1. directly
            if (item[0] + item[2]) > self.size[0] or (item[1] + item[3]) > self.size[1]:
                return 1.
        
            # multiply these rects and corresponding saliency roi
            temp_canva = np.zeros((self.size[1], self.size[0]), dtype='float')
            temp_canva[item[1]:item[1] + item[3], item[0]:item[0] + item[2]] = np.ones((item[3], item[2]), dtype='float')

            result += (bg_sal_copy * temp_canva)
        
        return np.mean(result)

    def eval_overlap(self):
        overlap_area_ratio = []
        def rect_overlap_area(rect1, rect2):
            # if rect not overlap, return 0
            if (rect1[0] + rect1[2] < rect2[0]) or (rect1[1] + rect1[3] < rect2[1]):
                return 0.
            
            if (rect2[0] + rect2[2] < rect1[0]) or (rect2[1] + rect2[3] < rect1[1]):
                return 0.
            
            # else return the overlapping area
            overlap_width = abs(min(rect1[0] + rect1[2], rect2[0] + rect2[2]) - max(rect1[0], rect2[0]))
            overlap_height = abs(min(rect1[1] + rect1[3], rect2[1] + rect2[3]) - max(rect1[1], rect2[1]))

            return overlap_width * overlap_height

        # calculate overlap ratio for every rect pair
        for i in range(len(self.rois)):
            for j in range(i+1, len(self.rois)):
                overlap_area = rect_overlap_area(self.rois[i], self.rois[j])
                overlap_area_ratio.append(overlap_area / (self.rois[i][2] * self.rois[i][3] + self.rois[j][2] * self.rois[j][3] - overlap_area))
        
        # regard max overlap ratio as the metric
        return max(overlap_area_ratio)

    def eval_third_rule(self):
        pass
    
    def eval_aesthetic(self):
        pass

    def eval_alignment(self):
        pass
