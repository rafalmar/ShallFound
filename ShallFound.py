

class Foot:
	concrete=25 #kN/m3
	
	
	def __init__(self, B, L, z, h):
		self.B=B
		self.L=L
		self.z=z
		self.h=h
		
	def stress(self, My, Mx, N, Hx, Hy, ex=0, ey=0):
		self.My=My
		self.Mx=Mx
		self.N=N
		self.Hx=Hx
		self.Hy=Hy
		self.ex=ex
		self.ey=ey
		
	def 
		
