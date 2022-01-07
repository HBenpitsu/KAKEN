with open("./exc_3*3cubable-pattern","r") as f:
	ps = [int(l[:-2],2) for l in f.readlines()]

def is_inclusive(a,b):
	c = a & b
	if a==c:
		return a
	elif b==c:
		return b
	else:
		return None

res=[]
for p in ps:
	inc = [is_inclusive(p,r) for r in res]
	res.append(p)
	for i in inc:
		if i in res:
			res.remove(i)
with open("exc_3*3cubable-pattern_inclusive_unifide","w") as f:
	for i in res:f.write(format(i,"0=9b")+"\n")
print(res)