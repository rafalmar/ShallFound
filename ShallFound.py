from borehole import Borehole
from math import exp, pi, radians, sin, cos, tan, fabs

class Foot:
	concrete=25 #kN/m3
	
	
	def __init__(self, typ, shape, B, L, h, z): #if the shape is circle input both B and L as Diameter
		self.typ=typ #foot / continous footing
		self.shape=shape
		self.B=B
		self.L=L
		self.z=z #bottom level
		self.h=h
		
		#initial loads
		self.Mz=0
		self.My=0
		self.V=B*L*h*25
		self.Hy=0
		self.Hz=0
		
		
		
	def add_loads(self, Mzc, Myc, V, Hy, Hz, ex=0, ey=0, ez=0): #Mzc is a bending moment in a column
		self.Mz=self.Mz + Mzc + V*ey + Hy*ex
		self.My=self.My + Myc + V*ez + Hz*ex
		self.V=self.V + V
		self.Hy=self.Hy + Hy
		self.Hz=self.Hz + Hz
		
		self.ey=self.Mz/self.V
		self.ez=self.My/self.V
		
		
	def load_BH(self, parameters, soils, bhProfile, level):
		
		Borehole.set_table(parameters, soils) # parametry to lista na przyklad [fi, c, gamma]
		
		self.bh=Borehole('profile', level, bhProfile).profil
		
		
	def apply_fill(self, kind, gamma=18.5, zasypki=[]):
		#kind = from_borehole / own
		if kind=="from_borehole":
			self.top_fill=self.bh['top'].max(axis=0)
			self.bottom_fill=self.z+self.h
			
			self.V+=(self.top_fill-self.bottom_fill)*gamma*self.B*self.L
		
				
		for zas in zasypki:
			self.V+=zas[0]*zas[1]*self.B*self.L
			
			print(self.bh)
			
			#SELECTING LAYER - PRZENIESC W INNE MIEJSCE
			"""
			if self.z < self.bh['bottom'].min(axis=0):
				print('foundation below soil investigation, lowest layer is being takeg to calculations')
				grunt=self.bh.iloc[-1]
				
			else:
				grunt=self.bh[(self.bh['bottom']<self.z) & (self.bh['top']>self.z)]
			print(grunt)
			"""
	def find_below(self):
		self.below=self.bh[self.bh['bottom']<self.z]
		self.below['top'][self.below.index.min()]=self.z
		self.below['thickness']=self.below['top']-self.below['bottom']
		print(self.below)
	
	def calculate_drained(self):
		results=self.below
		results['Nq']=exp(pi*tan(radians(results['fi'])))*(tan(radians(45+results['fi']/2)))^2 
		results['Nc']=(results['Nq']-1)/tan(radians(results['fi']))
		results['Ny']=2*(results['Nq']-1)*tan(radians(results['fi'])) # if delta > fi, means if the base is rough
		self.Bp=self.B-2*fabs(self.ey)
		self.Lp=self.L-2*fabs(self.ez)
		
		
		
		if self.shape=='circle':
			self.sq=1+sin(radians(results['fi']))
			self..sy=0.7
		else:
			self.sq=1+(self.Bp/self.Lp)*sin(radians(results['fi']))
			self.sy=1-0.3*(self.Bp/self.Lp)
		
		mb=(2+(self.Bp/self.Lp))/(1+(self.Bp/self.Lp))
		ml=(2+(self.Lp/self.Bp))/(1+(self.Lp/self.Bp))	

		
		if self.Hy==0 and self.Hz==0:
			self.iq=1
			self.ic=1
		else:
			if self.Hz==0 and self.Hy!=0:
				self.m=mb
			elif self.Hy==0 and self.Hz!=0:
				self.m=ml
			else:
				teta= # do opisania
				self.m=ml*cos(teta)**2+mb*sin(teta)**2
			
		
parameters=['gamma', 'Moed', 'fi', 'c']		
		
soils=[
		['gleba', 18, 34, 20, 1],
		['piasek', 19, 36, 34, 0],
		['glina', 21, 10, 15, 20],
		['organika', 10, 10, 5, 5]
		]
		
		
bh_1=[
		['gleba',0.5],
		['piasek',3],
		['glina',1],
		['organika', 5],
		['piasek',3]
		]

teren=0
posadowienie=-3
	
foot1=Foot(typ='foot', shape='rectangle', B=3, L=5, h=0.5, z=posadowienie)
foot1.add_loads(10, 20, 100, 3, 5, 1, 1)
foot1.load_BH(parameters, soils, bh_1, teren)
foot1.apply_fill(kind="from_borehole")
foot1.find_below()
foot1.calculate_drained
