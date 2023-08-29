class Metrics:
	def __init__(self):
		pass
	@staticmethod
	def get_average(iterator:iter)->float:
		n=0
		summation=0
		for x in iterator:
			if(x is None):
				continue
			if(x<=0):
				continue
			n+=1
			summation+=x
		return 0 if n==0 else round(summation/n,2)