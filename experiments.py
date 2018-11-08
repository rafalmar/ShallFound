import numpy as np
import random
from shapely.geometry import Polygon, Point
import seaborn as sns
import matplotlib.pyplot as plt


def get_random_point_in_polygon(poly, div):
	ps=[]
	(minx, miny, maxx, maxy) = poly.bounds
	for i in range(div):
		p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
		if poly.contains(p):
			ps.append(np.array(p))
	return np.array(ps)

p = Polygon([(0, 0), (0, 2), (1, 1), (2, 2), (2, 0), (1, 1), (0, 0)])
point_in_poly = get_random_point_in_polygon(p, 1000)
print(point_in_poly)
plt.plot(point_in_poly[:, 0], point_in_poly[:, 1], 'o', label = 'data')
plt.legend()
plt.show()