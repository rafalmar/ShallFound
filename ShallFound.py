from borehole import Borehole
from math import exp, pi, radians, sin, cos, tan, fabs
import numpy as np
from factors import GeoFactors

class Foot:
	concrete=25 #kN/m3
	fill=18.5
	
	
	def __init__(self, typ, shape, B, L, h, z, d1, d2, pfs, E1=0, E2=0): #if the shape is circle input both B and L as Diameter
		self.typ=typ #foot / Type by Schematy.dwg F1-F5
		self.shape=shape
		self.B=B
		self.L=L
		self.z=z #bottom level
		self.h=h
		self.pfs=pfs
		self.d1=d1 #collumn y dimension
		self.d2=d2 #collumn z dimension
		
		self.E1=E1
		
		
		#initial loads
		self.Mz=0
		self.My=0
		self.V=0
		self.Hy=0
		self.Hz=0
		
		self.Mzd=self.Mz
		self.Myd=self.My
		self.Vd=self.V
		self.Hyd=self.Hy
		self.Hzd=self.Hz
		
		osy=self.B/2
		osz=self.L/2
		
		G1={'B':self.B-osy-self.E1-self.d1/2,'L':self.L-osz-self.E2-self.d2/2,'V':0}
		G2={'B':self.B-osy-self.E1-self.d1/2,'L':self.L-G1['L']-self.d2,'V':0}
		G3={'B':self.B-G1['B']-self.d1,'L':G2['L'],'V':0}
		G4={'B':G3['B'],'L':G1['L'],'V':0}
		G5={'B':self.B-osy-self.E1-self.d1/2,'L':self.d2,'V':0}
		G6={'B':self.d1,'L':G1['L'],'V':0}
		G7={'B':G3['B'],'L':self.d2,'V':0}
		G8={'B':self.d1,'L':G2['L'],'V':0}
		
		G1['ez']=self.E1+self.d1/2+G1['B']/2
		G2['ez']=self.E1+self.d1/2+G2['B']/2
		G5['ez']=self.E1+self.d1/2+G5['B']/2
		G6['ez']=self.E1
		G8['ez']=self.E1
		G3['ez']=self.E1-self.d1/2-G3['B']/2
		G7['ez']=self.E1-self.d1/2-G7['B']/2
		G4['ez']=self.E1-self.d1/2-G4['B']/2
		
		G1['ey']=self.E2+self.d2/2+G1['L']/2
		G6['ey']=self.E2+self.d2/2+G6['L']/2
		G4['ey']=self.E2+self.d2/2+G4['L']/2
		G5['ey']=self.E2
		G7['ey']=self.E2
		G2['ey']=self.E2-self.d2/2-G2['L']/2
		G8['ey']=self.E2-self.d2/2-G8['L']/2
		G3['ey']=self.E2-self.d2/2-G3['L']/2
		
		self.G={'G1':G1, 'G2':G2, 'G3':G3, 'G4':G4, 'G5':G5, 'G6':G6, 'G7':G7, 'G8':G8}
		
		
	def apply_load_pfs(self, pfs):
		pass
	
		
	def add_loads(self, typ, Mzc=0, Myc=0, V=0, Hy=0, Hz=0, ex=0, ey=0, ez=0): #Mzc is a bending moment in a column
		self.Mz=self.Mz + Mzc + V*ey + Hy*ex
		self.My=self.My + Myc + V*ez + Hz*ex
		self.V=self.V + V
		self.Hy=self.Hy + Hy
		self.Hz=self.Hz + Hz
		
		self.ey=self.Mz/self.V
		self.ez=self.My/self.V
		
		if typ=="live":
			self.Mzd+=Mzc*self.pfs.A.q.sup + V*ey*self.pfs.A.q.sup + Hy*ex*self.pfs.A.q.sup
			self.Myd+= Myc*self.pfs.A.q.sup + V*ez*self.pfs.A.q.sup + Hz*ex*self.pfs.A.q.sup
			self.Vd+=V*self.pfs.A.q.sup
			self.Hyd+=Hy*self.pfs.A.q.sup
			self.Hzd+=Hz*self.pfs.A.q.sup
		elif typ=="dead":
			self.Mzd+=Mzc*self.pfs.A.g.sup + V*ey*self.pfs.A.g.sup + Hy*ex*self.pfs.A.g.sup
			self.Myd+= Myc*self.pfs.A.g.sup + V*ez*self.pfs.A.g.sup + Hz*ex*self.pfs.A.g.sup
			self.Vd+=V*self.pfs.A.g.sup
			self.Hyd+=Hy*self.pfs.A.g.sup
			self.Hzd+=Hz*self.pfs.A.g.sup
		
		
	def load_BH(self, parameters, soils, bhProfile, level):
		
		Borehole.set_table(parameters, soils) # parametry to lista na przyklad [fi, c, gamma]
		
		self.bh=Borehole('profile', level, bhProfile).profil
		
		
	def apply_fill(self, where, side, gamma=18.5, top=self.bh['top'].max(axis=0), zasypki=[]):
		#defaultowo dodaje zasypkę jednowarstwową do poziomu terenu
		#opcjonalnie można zmienić poziom zasypki oraz podzielić ją na warstwy
		#where mówi do których pól przyłożyć daną zasypkę rodzajem obciążenia wg Schemat.dxf i służy do właściwego przydzielenia obciążeń G1...G8
		# FUNKCJA WYMAGA POPRAWIENIA, NIE UWZGLĘDNIA MIMOŚRODU, POWINNA MIEĆ WIĘCEJ OPCJI DODAWANIA ZASYPKI
		zasypki=np.array(zasypki)
		self.bottom_fill=self.z+self.h

		
		if len(zasypki)==0:
			#then assume there is only one layer of backfill to the level of 'top' variable
			g=(self.top_fill-self.bottom_fill)*gamma
		else:
			g=np.prod(zasypka, axis=1).sum()
		
		for i in where:
			dG=self.G[i]['B']*self.G[i]['L']*g
			self.G[i]['V']+=dG
			
			self.V+=dG
			self.Vd+=dG*self.pfs.A.g.sup
			self.My
		
		
		
		for zas in zasypki:
			self.V+=zas[0]*zas[1]*self.B*self.L
			self.Vd+=zas[0]*zas[1]*self.B*self.L*self.pfs.A.g.sup
			
			
			
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
		#ey ex need to be reaclucated afeter adding fill
		self.ey=self.Mz/self.V
		self.ez=self.My/self.V
		
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
		results['Vd']=0
		results['A']=results['B']*results['L']
		
		#print(results.shape[0])
		
		for i in range(1, results.shape[0]):
			results.iloc[i, results.columns.get_loc('V')]=results.iloc[i-1, results.columns.get_loc('thickness')]*results.iloc[i-1, results.columns.get_loc('gamma')]*results.iloc[i, results.columns.get_loc('A')]
			results.iloc[i, results.columns.get_loc('Vd')]=results.iloc[i-1, results.columns.get_loc('thickness')]*results.iloc[i-1, results.columns.get_loc('gamma')]*results.iloc[i, results.columns.get_loc('A')]*self.pfs.A.g.sup
		results['V']=results['V'].cumsum()+self.V
		results['Vd']=results['Vd'].cumsum()+self.Vd

		results['ey']=self.Mz/results['V']
		results['ez']=self.My/results['V']

		results['Bp']=results['B']-results['ey']
		results['Lp']=results['L']-results['ez']


		
		if self.shape=='circle':
			results['sq']=results['fi'].apply(lambda x: 1+sin(radians(x)))
			self.sy=0.7
		else:
			
			results['sq']=results.apply(lambda x: 1+ x['Bp']/x['Lp']*sin(radians(x['fi'])), axis=1)

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
			
			#FRAGMENT ODPOWIEDZIALNY ZA POZYTYWNY WPLYW GRUNTU OBOK FUNDAMENTU - TRZEBA WYBRAC DO OBLICZEN STRONE FUNDAMENTU W ZALEZNOSCI OD MOMENTU, na razie nie ma znaczenia bo liczy zasypke do poziomu terenu
			#DO SPRAWDZENIA CZY CUMSUM LICZY DOBRZE - CZY MA SENS
			results['rq']=(self.top_fill-self.bottom_fill)*type(self).fill
			for i in range(results.shape[0]-1):
				results['rq'].iloc[i+1]=results['thickness'].iloc[i]*results['gamma'].iloc[i]
			results['rq']=results['rq']*results['Nq']*1*results['sq']*results['iq']
			results['rq']=results['rq'].cumsum()
			
			
			
			results['ry']=0.5*results['gamma']*results['Bp']*1*results['sy']*results['iy']
			#results['rq'].iloc[0, results.columns.get_loc('rq')]=0
			results['R']=results['rc']+results['rq']+results['ry']
			results['eyd']=self.Mzd/results['Vd']
			results['ezd']=self.Myd/results['Vd']
			results['Bpd']=results['B']-results['eyd']
			results['Lpd']=results['L']-results['ezd']
			results['Apd']=results['Bpd']*results['Lpd']
			results['mi']=(results['Vd']/results['Apd'])/results['R']
			self.results=results
			
		#print(results)
		#print(results[['thickness','gamma','B','L','c','rc']])
	

#PARTIAL FACTORS
pf=GeoFactors("DA2*")


	
		
parameters=['gamma', 'Moed', 'fi', 'c']		


		
soils=[
		['gleba', 18, 34, 20, 1],
		['piasek', 19, 36, 34, 0],
		['glina', 21, 10, 15, 20],
		['organika', 10, 10, 5, 5]
		]

soilsd=soils		
for soild in soilsd:
	soild[parameters.index('fi')+1]*=pf.M.fi
	soild[parameters.index('c')+1]*=pf.M.c
	soild[parameters.index('gamma')+1]*=pf.M.g
		
bh_1=[
		['gleba',0.5],
		['piasek',3],
		['glina',1],
		['organika', 5],
		['piasek',3]
		]

terrain_level=0
posadowienie=-3.5





	
foot1=Foot(typ='F1', shape='rectangle', B=3, L=5, h=0.5, z=posadowienie, pfs=pf)
foot1.add_loads(typ='dead', Mzc=10, Myc=20, V=100, Hy=3, Hz=5, ex=1, ey=1)


foot1.load_BH(parameters, soils, bh_1, terrain_level)
foot1.apply_fill(kind="from_borehole", side='left' ,gamma=18.5)
foot1.find_below()
foot1.calculate_drained()
print(foot1.results)

