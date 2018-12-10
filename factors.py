from dotmap import DotMap

class GeoFactors():
	A1={'g':{'sup':1.35, 'inf':1.0}, 'q':{'sup':1.5, 'inf':0}, 'a':{'sup':1.0, 'inf':1.0}}
	A2={'g':{'sup':1.0, 'inf':1.0}, 'q':{'sup':1.3, 'inf':0}, 'a':{'sup':1.0, 'inf':1.0}}
		
	M1={'fi':1.0, 'c':1.0, 'cu':1.0, 'qu':1.0, 'g':1.0}
	M2={'fi':1.25, 'c':1.25, 'cu':1.4, 'qu':1.4, 'g':1.0}
		
	R1={'v':1.0, 'h':1.0}
	R2={'v':1.4, 'h':1.1}
	R3={'v':1.0, 'h':1.0}

	def __init__(self, da=None):
		
		self.da = da
		if self.da=="DA2*":
			self.A=DotMap(self.A1)
			self.M=DotMap(self.M1)
			self.R=DotMap(self.R2)
		elif self.da=="DA1.C1":
			self.A=DotMap(self.A1)
			self.M=DotMap(self.M1)
			self.R=DotMap(self.R1)
		elif self.da=="DA1.C2":
			self.A=DotMap(self.A2)
			self.M=DotMap(self.M2)
			self.R=DotMap(self.R1)
		


if __name__=="__main__":
			
	pf=GeoFactors("DA2*")
	print(pf.A.g.sup)
