from borehole import Borehole

class Foot:
	concrete=25 #kN/m3
	
	
	def __init__(self, typ, B, L, h, z):
		self.typ=typ #foot / continous footing
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
		
		
	def load_BH(self, soils, bhProfile, level):
		parameters=['gamma', 'Moed']
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
	
	def calculate():
		pass
		
		
soil_props=[
		['gleba', 18, 34],
		['piasek', 19, 36],
		['glina', 21, 10],
		['organika', 10, 10]
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
	
foot1=Foot(typ='foot', B=3, L=5, h=0.5, z=posadowienie)
foot1.add_loads(10, 20, 100, 3, 5, 1, 1)
foot1.load_BH(soil_props, bh_1, teren)
foot1.apply_fill(kind="from_borehole")
foot1.find_below()

