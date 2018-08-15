import numpy as np
import pandas as pd
import itertools

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
		
		#print(self.profil)
		#self._datalen=self.profil["top"].max - self.profil['bottom'].min
		
		
	
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
		return self.profil["top"].max() - self.profil['bottom'].min()  # TU JEST BŁĄD, __LEN__ CHYBA NIE MOŻE ZWRÓCIĆ FLOAT'A NAWET PO OVERRIDZIE
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
		self.p1.X=0
		self.p2.X=self.p1.X+dist
		self.p1=p1
		self.p2=p2
		self.dist=dist
		self.dim=dim
		
		self.p1.profil['mid']=(self.p1.profil['top']+self.p2.profil['bottom'])/2
		self.p2.profil['mid']=(self.p2.profil['top']+self.p2.profil['bottom'])/2
		
		self.topL=p1.profil['top'].max()
		self.topR=p2.profil['top'].max()
		self.botL=p1.profil['bottom'].min()
		self.botR=p2.profil['bottom'].min()
		
		self.uniques=list(self.p1.profil['name'].unique())
		self.uniques.extend(list(self.p2.profil['name'].unique()))
		self.uniques=list(set(self.uniques))
		
		print(self.uniques)
		self.test2d()
		
	def test2d(self):	
		
		self.nx=int(self.dist//self.dim)+1
		
		self.maxy=max(self.topL, self.topR)
		self.miny=min(self.botR, self.botL)
		self.ny=int((self.maxy-self.miny)//self.dim)+1
		x =[0+i*self.dim for i in range(self.nx+1)]
		y =[self.maxy-i*self.dim for i in range(self.ny+1)]
		xy=itertools.product(x, y)
		#print(x)
		#print(list(xy))
		for i in xy:
			i=list[i]
			rL=((i[0]-self.p1.X)**2+(i[1]-self.p1.profil['mid'])**2)**0.5
			rR=((i[0]-self.p2.X)**2+(i[1]-self.p2.profil['mid'])**2)**0.5
		
	
		
		
		
		
		
		
		
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
	['gleba',0.5],
	['piasek',3],
	['gleba',1],
	['glina', 5]
	]
	
	otwor2=[
	
	['piasek',1],
	['gleba',1],
	['organika',2],
	['glina', 5]
	]
	
	
	
	bh1=Borehole('o1',100, otwor1)
	bh2=Borehole('o2',101, otwor2)
	#pr=Section2d(bh1,bh2,10, 0.2)
	
	print(bh1.profil)
	print(bh2.profil)
	
	"""
	cs1=Section(bh1.profil, bh2.profil)
	print(cs1.cs)
	"""

