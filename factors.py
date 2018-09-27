

class PartialFactors():
	
	__EC7={'DA1':{'M':1,'A':1, 'R':1}}
	
	def __init__(self, norm, da=None):
		self.norm=norm
		self.da=da
		if self.da!=None:
			__factors=self.__EC7[da]
			print(__factors)
			return(__factors)
	def sup(self):
		pass
	def inf(self):
		pass
		
test_f=PartialFactors("EC","DA1")

#wymyslic sposób na wybór normy i w związku z tym odpowiedniego słownika ze zmiennych klasowych