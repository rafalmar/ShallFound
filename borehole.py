import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="whitegrid")
import itertools
import time
import random
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')





# baza nazw: [fi, c, gamma, M0, E0]

class Borehole:
	
	__defaults={'level':0.0}

	def __init__(self, name, level, bhlist):
		self.level=level
		self.name=name
		
		self.profil=pd.DataFrame(list(bhlist), columns=['name', 'thickness'])
		self.profil['bottom']=self.level-self.profil['thickness'].cumsum()
		self.profil['top']=self.profil['bottom']+self.profil['thickness']
		self.match_gnds()
		
		
	
	@property
	def level(self):
		return self.__level
	@level.setter
	def level(self, level):
		try:
			self.__level=float(level)
		except:
			self.__level=Borehole.__defaults['level']
	def len(self):
		return self.profil["top"].max() - self.profil['bottom'].min()
	@classmethod
	def set_table(cls, params, grounds):
		params.insert(0, "name")
		n=len(params)
		try:
			cls.__groundstable=pd.DataFrame(grounds, columns=params)
		except Exception as exc:
			print(exc)
			print("Check length of parameters")
			cls.__groundstable=None
	@classmethod			
	def get_table(cls):
		return(cls.__groundstable)
		
	def match_gnds(self):
		try:
			self.profil=pd.merge(self.profil, type(self).__groundstable, on='name', how='left')
			return self.profil
		except Exception as exc:
			print(exc)
			print('couldn\'t match groundstable to profile')
	def test(self):
		print(self.__groundstable)
		
		

		
class Section2d():
	def __init__(self, p1, p2, dist, dim):
		self.p1=p1
		self.p2=p2
		self.p1.X=0
		self.p2.X=self.p1.X+dist
		
		self.dist=dist
		self.dim=dim
		
		self.p1.profil['mid']=(self.p1.profil['top']+self.p1.profil['bottom'])/2
		self.p2.profil['mid']=(self.p2.profil['top']+self.p2.profil['bottom'])/2
		
		self.topL=p1.profil['top'].max()
		self.topR=p2.profil['top'].max()
		self.botL=p1.profil['bottom'].min()
		self.botR=p2.profil['bottom'].min()
		
		self.uniques=list(self.p1.profil['name'].unique())
		self.uniques.extend(list(self.p2.profil['name'].unique()))
		self.uniques=list(set(self.uniques))
		
		print(self.uniques)
		print(self.p1.profil)
		self.test2d(10)
		
	def test2d(self, div):	
				
		
		polygon=Polygon([(0, self.topL), (self.dist, self.topR), (self.dist,self.botR), (0,self.botL), (0,self.topL)])
		point_in_poly = self.get_random_point_in_polygon(polygon, 3000)
		
		p_in_poly=pd.DataFrame(point_in_poly, columns=['x','y'])
		#p_in_poly['xy']=pd.DataFrame.apply(lambda x: np.array([[x['x'], x['y']]]))

		self.p1.profil['x']=0
		self.p2.profil['x']=self.dist

		df=self.p1.profil.append(self.p2.profil, ignore_index=True)

		for i in self.uniques:
			df2=df[df['name']==i][['x','mid', 'thickness']]
			p_in_poly[i]=p_in_poly.apply(lambda row: self.func(row, df2), axis=1)




		print(df[['x','mid','thickness']])
		
		p_in_poly['match']=p_in_poly[self.uniques].idxmax(axis=1)
		
		
		print(p_in_poly.head())
		
		
		sns.scatterplot(data=p_in_poly, x='x', y='y', hue='match')
		plt.show()
		
	def func(self, row, other):
		#other_value = other.loc[x.name]
		x=row['x']		
		y=row['y']
		other['r']=other.apply(lambda n: ((n['x']-x)**2+(n['mid']-y)**2)**0.5, axis=1)
		
		A=1 #waga masy
		B=1 #waga odleglosci
		C=1	#waga kata
		
		
		
		other['weight1']=A* other['thickness']																#POMYSL 1 masy
		other['weight2']=1/(other['r']**B)																	#POMYSL 2 wplyw odleglosci
		other['weight3']=C * other.apply(lambda n: 1/(np.absolute(n['mid']-y)/np.absolute(n['x']-x))/len(other.index), axis=1) 	#POMYSL 3 wplyw 1/sin()
		
		other['weight']=other['weight2']
		
		
		#NOWY POMYSL - PRZYCIAGAC NIE TYLKO DO SRODKA ALE TEZ DO ROGOW WARSTWY
		
		return other['weight'].sum()
	
	def get_random_point_in_polygon(self, poly, div, pnt=False):
		ps=[]
		(minx, miny, maxx, maxy) = poly.bounds
		while len(ps)<div:
			p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
			if poly.contains(p):
				ps.append(np.array(p))
		ps=np.array(ps)
		if pnt==True:
			plt.plot(ps[:, 0], ps[:, 1], 'o', label = 'data')
			plt.legend()
			plt.show()
		return ps

		
		
		
		
		
"""

class Section():
	def __init__(self, left, right):
		self.left=left
		self.right=right
		self.match2bhs()
		
	def match2bhs(self):
		
		
		self.nL=self.left.shape[0] #count of left layers
		#self.nuL=self.left[self.left.columns[0]].nunique() #count of left unique layers
		
		self.nR=self.right.shape[0] #count of right layers
		#self.nuP=self.right[self.right.columns[0]].nunique() #count of right unique layers

				
		self.cs=pd.DataFrame([['surface',  self.left.iloc[0]['top'], self.right.iloc[0]['top']]], columns=['layer', 'left', 'right'])
		
		i=0
		j=0
		
		while i<self.nL and j<self.nR:
			if self.left.iloc[i]['name']==self.right.iloc[j]['name']:
				row=pd.DataFrame(self.left.iloc)
				self.cs.append

"""



	
if __name__=="__main__":		
	
	# At the beginning you should always define table of all grounds and their parameters
	# If not defined, method .match_gnds() should be used on every single borehole object
	parametry=['gamma','fi','c']
	grunty=[
	['gleba', 18, 34, 4],
	['piasek', 19, 36, 0],
	['glina', 21, 10, 40],
	['organika', 10, 10, 10]
	]
	
	Borehole.set_table(parametry, grunty) # parametry to lista na przyklad [fi, c, gamma]
	
	
	otwor1=[
	['gleba',2],
	['organika',2],
	['piasek',2],
	['glina', 4]
	]
	
	otwor2=[
	
	['gleba',2],
	['organika',2],
	['piasek',2],
	['glina', 4]
	]
	
	
	
	bh1=Borehole('o1',100, otwor1)
	bh2=Borehole('o2',100, otwor2)
	#pr=Section2d(bh1,bh2,10, 0.2)
	
	print(bh1.profil)
	print(bh2.profil)
	
	
	cs1=Section2d(bh1, bh2, 10, 0.1)

	

