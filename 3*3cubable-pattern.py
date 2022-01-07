bins = lambda x:format(x,"0=9b")
def invert(ts:str):
	return (
		ts[6:8]+
		ts[3:5]+
		ts[0:2]
	)
def rotate(ts:str):
	return (
		ts[6]+ts[3]+ts[0]+
		ts[7]+ts[4]+ts[1]+
		ts[8]+ts[5]+ts[2]
	)
def are_symmetry(a:str,b:str):
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
res=[]
for i in range(2**9):
	break_the_1st_rule=[0b110110000,0b011011000,0b000011011,0b000110110]
	if bin(i).count("1")<7:
		if not any([bin(i&b).count("1")==4 for b in break_the_1st_rule]):
			if not any([are_symmetry(b,bins(i)) for b in res]):
				res.append(bins(i))
with open("exc_3*3cubable-pattern","w") as f:
	for i in res:f.write(i+"\n")
print(res)