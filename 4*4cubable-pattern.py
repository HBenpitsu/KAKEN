import datetime
previous = datetime.datetime.now()

bins = lambda x:format(x,"0=16b")
def invert(ts:str):
	return (
		ts[12:16]+
		ts[4:8]+
		ts[8:12]+
		ts[0:4]
	)
def rotate(ts:str):
	return (
		ts[12]+ts[8]+ts[4]+ts[0]+
		ts[13]+ts[9]+ts[5]+ts[1]+
		ts[14]+ts[10]+ts[6]+ts[2]+
		ts[15]+ts[11]+ts[7]+ts[3]
	)
def are_symmetry(a:str,b:str):
	if a.count("1") != b.count("1"):
		return False
	for _ in range(4):
		b=rotate(b)
		if a==b:
			return True
	invert(b)
	for _ in range(4):
		b=rotate(b)
		if a==b:
			return True
	return False


#def are_symmetry_or_inclusive(a:str,b:str):
#	"""
#	if either of arguments'symmetric include the other,this function return True,[bigger],[smaller].
#	if not,this return False,a,b
#	"""
#	for _ in range(4):
#		b=rotate(b)
#		incl=are_inclusive(a,b)
#		if incl[0]:
#			return incl
#	invert(b)
#	for _ in range(4):
#		b=rotate(b)
#		incl=are_inclusive(a,b)
#		if incl[0]:
#			return incl
#	return False,0
#def are_inclusive(a:str,b:str):
#	"""
#	if either of arguments include the other,this function return True,-1/1.(When a include b 2nd argument is 1)
#	if not,this return False,0.
#	"""
#	ai=int(a,2)
#	bi=int(b,2)
#	if ai&bi==ai:
#		return True,-1
#	elif ai&bi==bi:
#		return True,1
#	return False,0

class SqMask:
	def __init__(self,mask,shift_number):
		self.masks=[]
		for _ in range(shift_number):
			for i in range(shift_number):
				self.masks.append(mask>>i)
			mask>>=4
	def biggest_match(self,target:int):
		res=0
		for m in self.masks:
			res=max(bin(target&m).count("1"),res)
		return res
res=[]
first_rule_mask=SqMask(0b1100110000000000,3)
second_rule_mask=SqMask(0b1110111011100000,2)

for i in range(2**16):
	if bins(i).count("1")>=6:
		if second_rule_mask.biggest_match(i)<7:
			if first_rule_mask.biggest_match(i)<4:
				if not any([are_symmetry(b,bins(i)) for b in res]):
					res.append(bins(i))
			#i_append=True
			#for r in res[::]:
			#	inc = are_symmetry_or_inclusive(bins(i),r)
			#	if inc[0]:
			#		if inc[1]==1:
			#			res.remove(r)
			#		elif inc[1]==-1:
			#			i_append=False
			#			break
			#if i_append:
			#	res.append(bins(i))

with open("exc_4*4cubable-pattern","w") as f:
	for i in res:f.write(i+"\n")
	f.write(str("this process takes",datetime.datetime.now()-previous))