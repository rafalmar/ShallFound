from borehole import Borehole
from math import exp, pi, radians, sin, cos, tan, fabs
import numpy as np

class Foot:
	concrete=25 #kN/m3
	fill=18.5
	
	
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
		self.V=B*L*h*type(self).concrete
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
		self.below=self.bh[self.bh['bottom']<self.z].copy()
		self.below.iloc[0,self.below.columns.get_loc('top')]=self.z
		self.below['thickness']=self.below['top']-self.below['bottom']
		#print(self.below)
	
	def calculate_drained(self):
		self.Bp=self.B-2*fabs(self.ey)
		self.Lp=self.L-2*fabs(self.ez)
		results=self.below
		results['Nq']=results['fi'].apply(lambda x: exp(pi*tan(radians(x)))*(tan(radians(45+x/2)))**2)
		results['Nc']=results['Nq'].apply(lambda x: (x-1)/tan(radians(x)))
		results['Ny']=results.apply(lambda x: 2*(x['Nq']-1)*tan(radians(x['fi'])), axis=1) # if delta > fi, means if the base is rough
		results['B']=self.B
		results['L']=self.L
		bq=1
		bc=1
		
		# ZMIENIC ZALOZENIE - poszerzenie podstawy "b" dodawac do B i L w kolejnych warstwach a nie do Bp i Lp. Bp i Lp wyliczac od nowa na podstawie nowych
		#mimosrodow wynikajacych z dodania ciezaru warstwy wyzszej
		
		B=results.iloc[0,results.columns.get_loc('B')]
		L=results.iloc[0,results.columns.get_loc('L')]
		#print(self.Bp)
		for i in range(1, results.shape[0]):
			c=results.iloc[i-1,results.columns.get_loc('c')]
			h=results.iloc[i-1,results.columns.get_loc('thickness')]
			
			if h<=B:
				if c>0:
					b=h/4
				else:
					b=h/3
			else:
				if c>0:
					b=h/3
				else:
					b=2*h/3
			B+=b
			L+=b
			results.iloc[i, results.columns.get_loc('B')]=B
			results.iloc[i, results.columns.get_loc('L')]=L
		


		results['V']=0
		results['A']=results['B']*results['L']
		
		#print(results.shape[0])
		
		for i in range(1, results.shape[0]):
			results.iloc[i, results.columns.get_loc('V')]=results.iloc[i-1, results.columns.get_loc('thickness')]*results.iloc[i-1, results.columns.get_loc('gamma')]*results.iloc[i, results.columns.get_loc('A')]
		results['V']=results['V'].cumsum()+self.V


		results['ey']=self.Mz/results['V']
		results['ez']=self.My/results['V']

		results['Bp']=results['B']-results['ey']
		results['Lp']=results['L']-results['ez']








		

		
		if self.shape=='circle':
			results['sq']=results['fi'].apply(lambda x: 1+sin(radians(x)))
			self.sy=0.7
		else:
			# TU JEST DO POPRAWY, PRZEROBIĆ PONIŻSZE DO DATAFRAMEA
			results['sq']=results.apply(lambda x: 1+ x['Bp']/x['Lp']*sin(radians(x['fi'])), axis=1)
			#self.sq=1+(self.Bp/self.Lp)*sin(radians(results['fi']))
			
			#self.sy=1-0.3*(self.Bp/self.Lp)
			results['sy']=results.apply(lambda x: 1-0.3*x['Bp']/x['Lp'], axis=1)
		results['sc']=(results['sq']*results['Nq']-1)/(results['Nq']-1)
		results['mb']=results.apply(lambda x: (2+x['Bp']/x['Lp'])/(1+x['Bp']/x['Lp']), axis=1)
		results['ml']=results.apply(lambda x: (2+x['Lp']/x['Bp'])/(1+x['Lp']/x['Bp']), axis=1)
		
		
		
		if self.Hy==0 and self.Hz==0:
			
			results['iq']=1
			results['ic']=1
		else:
			H=np.array([self.Hy,self.Hz])
			Hnorm=np.sqrt(H.dot(H))
			if self.Hz==0 and self.Hy!=0:
				#self.m=mb
				results['m']=results['mb']
			elif self.Hy==0 and self.Hz!=0:
				#self.m=ml
				results['m']=results['mb']
			else:
				
				
				
				costeta=(np.dot(H,np.array([0,1])))/Hnorm/1
				if costeta>0:
					teta= np.arccos(costeta)
				else:
					teta=pi-np.arccos(costeta)
				#self.m=ml*cos(teta)**2+mb*sin(teta)**2
				results['m']=results.apply(lambda x: x['ml']*cos(teta)**2+x['mb']*sin(teta)**2, axis=1)
			results['iq']=(1-(Hnorm/(results['V']+results['Bp']*results['Lp']*results['c']*results['fi'].apply(radians).apply(tan).apply(lambda x: 1/x))))**results['m'] # to musi być kolumna w tabeli zamiast stałej wartości bo zależy od C
			results['ic']=results['iq']-(1-results['iq'])/results['Nc']/results['fi'].apply(radians).apply(tan)
			results['iy']=(1-(Hnorm/(results['V']+results['Bp']*results['Lp']*results['c']*results['fi'].apply(radians).apply(tan).apply(lambda x: 1/x))))**(results['m']+1) # to musi być kolumna w tabeli zamiast stałej wartości bo zależy od C
		
			results['rc']=results['c']*results['Nc']*bc*results['sc']*results['ic']
			
			results['rq']=(self.top_fill-self.bottom_fill)*type(self).fill
			for i in range(results.shape[0]-1):
				results['rq'].iloc[i+1]=results['thickness'].iloc[i]*results['gamma'].iloc[i]
			results['rq']=results['rq']*results['Nq']*1*results['sq']*results['iq']
			results['rq']=results['rq'].cumsum()
			results['ry']=0.5*results['gamma']*results['Bp']*1*results['sy']*results['iy']
			#results['rq'].iloc[0, results.columns.get_loc('rq')]=0
			results['R']=results['rc']+results['rq']+results['ry']
			results['SF']=results['R']/(results['V']/results['Bp']/results['Lp'])
			
		print(results)
		#print(results[['thickness','gamma','B','L','c','rc']])

		
		
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
posadowienie=-3.5
	
foot1=Foot(typ='foot', shape='rectangle', B=3, L=5, h=0.5, z=posadowienie)
foot1.add_loads(10, 20, 100, 3, 5, 1, 1)
foot1.load_BH(parameters, soils, bh_1, teren)
foot1.apply_fill(kind="from_borehole", gamma=18.5)
foot1.find_below()
foot1.calculate_drained()
