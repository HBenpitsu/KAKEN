import warnings
import itertools
#Why didn't you use numpy!?incredible...
"""
coordinate system:
to up:axis y+, to down:axis y-
to left:axis x+,to right:axis x-
to front:axis z+,to back:axis z-
rotate system:
looking origin from x plus side,anti-clockward rotation is +x,clockward rotation is -x.
looking origin from y plus side,anti-clockward rotation is +x,clockward rotation is -y.
looking origin from z plus side,anti-clockward rotation is +x,clockward rotation is -z.

for visualize,refer to 'Datastructure.png'
"""

def direction_str_cast_to_vector(direction:str):
	"""
	casting the infomation as charactor to vector3.\n
	"""	
	if isinstance(direction,str):
		if len(direction)!=1 or not direction in "rludfbi":
			raise ValueError(f"direction must be unit-vector3,0-vector or one of the chars:'rludfbi',but {direction} was passed.")
		direction={"r":(1,0,0),"l":(-1,0,0),"u":(0,1,0),"d":(0,-1,0),"f":(0,0,1),"b":(0,0,-1),"i":(0,0,0)}[direction]
	elif isinstance(direction,tuple):
		if len(direction)!=3:
			raise ValueError(f"direction must be unit-vector3,0-vector or one of the chars:'rludfbi',but {direction} was passed.")
	return direction
def perpendicular_rotate(axis:str,basex,basey,basez,posx,posy,posz,times=1):
	"""
	axis:x,y,z\n
	this is sight position.e.g. x being passed means this supply x rotation. \n
	also,it can be designated basis-vectors.\n
	if a vector which has negative element is passed,negative element will be dealt as its absolute.\n
	
	times: \n
	times<0;it's mean muinus(clockward) rotation.\n
	abs(times)>1; the result is the same with apply this function [times] times.'\n
	
	base:\n
	this is center of rotation\n
	
	pos:\n
	this is target of rotation\n
	"""
	while times != 0:
		if axis=="x" or isinstance(axis,tuple) and tuple(map(abs,axis))==(1,0,0):
			if times>0:
				posy,posz=(posz-basez)+basey,-(posy-basey)+basez
			if times<0:
				posy,posz=-(posz-basez)+basey,(posy-basey)+basez
		elif axis=="y" or isinstance(axis,tuple) and tuple(map(abs,axis))==(0,1,0):
			if times>0:
				posx,posz=-(posz-basez)+basex,(posx-basex)+basez
			if times<0:
				posx,posz=(posz-basez)+basex,-(posx-basex)+basez
		elif axis=="z" or isinstance(axis,tuple) and tuple(map(abs,axis))==(0,0,1):
			if times>0:
				posx,posy=(posy-basey)+basex,-(posx-basex)+basey
			if times<0:
				posx,posy=-(posy-basey)+basex,(posx-basex)+basey
		else:
			raise ValueError(f"axis must be x,y or z,not {axis}")
		#reduce absolute value of `times`
		times+=(2*(times<0)-1)*(times!=0)
	return posx,posy,posz
MODEL_DISTANCE={"f":float(str((1.5**2+1.5**2)**0.5)[:10]),"F":2,"0":1,"R":2,"r":float(str((0.5**2+0.5**2)**0.5)[:10])}
MODEL_DISTANCE_R={float(str((0.5**2+0.5**2)**0.5)[:10]):"r",1:"0",float(str((1.5**2+1.5**2)**0.5)[:10]):"f",2:"FR"}
#to take the ten upper digtis in order to measures against rounding error
ROTATION_TIMES_AT_r_AND_POSITIVE_POSITION_TABLE = {
	(1,0,0):{(0,1,0):1,(0,0,1):-1,(0,-1,0):-1,(0,0,-1):1},
	(0,1,0):{(0,0,1):1,(1,0,0):-1,(0,0,-1):-1,(-1,0,0):1},
	(0,0,1):{(1,0,0):1,(0,1,0):-1,(-1,0,0):-1,(0,-1,0):1}
}#[rotation axis][square direction]
#ROTATION_TIMES_AT_r_AND_POSITIVE_POSITION_TABLE[`rotation axis`][`squaredirection`]*`positional state`

class Square:
	def __init__(self,posx:int,posy:int,posz:int,direction:str,headway:str,mode:str,identity:int):
		"""
		pos is cebter of the square\n
		direction is one of basis vectors or negative one\n
		headway helps indicate relation around\n
		mode is one of "R","r","0","f","F"\n
		identity is to identify this instance on Origami
		"""
		self.identity=identity
		self.pos=posx,posy,posz
		self.direction=direction_str_cast_to_vector(direction)
		self.headway=direction_str_cast_to_vector(headway)
		self.fixed_side=None
		self.outside_level=0
		self.executed=False
		self.next_to={"t":None,"b":None,"l":None,"r":None}
		if not mode in "Rr0fF":
			raise ValueError("mode must be char:one of \"Rr0fF\",not {}".format(mode))
		self.mode=mode
	def direction_of_upsquare(self):
		if (self.mode in "RF" and self.fixed_side in "br") or (self.mode in "rf" and self.fixed_side in "bl"):
			return tuple(map(lambda x:-x,self.direction))#-1*self.direction
		else:#if (self.mode in "RF" and self.fixed_side in "lt") or (self.mode in "rf" and self.fixed_side in "tr")
			return self.direction
	def direction_of_rightsquare(self):
		if (self.mode in "RF" and self.fixed_side in "lt") or (self.mode in "rf" and self.fixed_side in "bl"):
			return tuple(map(lambda x:-x,self.direction))#-1*self.direction
		else:#if (self.mode in "RF" and self.fixed_side in "br") or (self.mode in "rf" and self.fixed_side in "tr")
			return self.direction
	def direction_of_square_on(self,way:str):
		"""way is one of the "rt",not"lb"."""
		if way=="r":
			return self.direction_of_rightsquare()
		elif way=="t":
			return self.direction_of_upsquare()
		else:
			raise ValueError
	def headway_of_upsquare(self):
		return self.upward()
	def headway_of_rightsquare(self):
		return perpendicular_rotate(self.direction,0,0,0,*self.rightward(),sum(self.direction_of_rightsquare()))
	def headway_of_square_on(self,way:str):
		"""way is one of the "rt",not"lb"."""
		if way=="r":
			return self.headway_of_rightsquare()
		elif way=="t":
			return self.headway_of_upsquare()
		else:
			raise ValueError
	def upward(self):
		if self.mode in "RF" and self.fixed_side in "br":
			return perpendicular_rotate(self.direction,0,0,0,*self.headway,-sum(self.direction))
		elif self.mode in "rf" and self.fixed_side in "lb":
			return perpendicular_rotate(self.direction,0,0,0,*self.headway,sum(self.direction))
		else:
			return self.headway
	def rightward(self):
		if self.mode in "RF" and self.fixed_side in "lt":
			return self.headway
		elif self.mode in "rf" and self.fixed_side in "lb":
			return tuple(map(lambda x:-x,self.headway))
		else:
			return perpendicular_rotate(self.direction,0,0,0,*self.headway,-sum(self.direction))
	def downward(self):
		if self.mode in "RF" and self.fixed_side in "lt":
			return perpendicular_rotate(self.direction,0,0,0,*self.headway,-sum(self.direction))
		elif self.mode in "rf" and self.fixed_side in "tr":
			return perpendicular_rotate(self.direction,0,0,0,*self.headway,sum(self.direction))
		else:
			return tuple(map(lambda x:-x,self.headway))
	def leftward(self):
		if self.mode in "RF" and self.fixed_side in "br":
			return tuple(map(lambda x:-x,self.headway))
		elif self.mode in "rf" and self.fixed_side in "tr":
			return self.headway
		else:
			return perpendicular_rotate(self.direction,0,0,0,*self.headway,sum(self.direction))
	def differ_to(self,way:str):
		"""way is one of the "rtlb"."""
		if way=="r":
			return self.rightward()
		elif way=="t":
			return self.upward()
		elif way=="b":
			return self.downward()
		elif way=="l":
			return self.leftward()
		else:
			raise ValueError
	def rotate(self,axis,basex,basey,basez,times=1):
		if self.executed is True:
			warnings.warn("excuted Square was rotated")
		self.headway = perpendicular_rotate(axis,0,0,0,*self.headway,times)
		self.direction = perpendicular_rotate(axis,0,0,0,*self.direction,times)
		self.pos = perpendicular_rotate(axis,basex,basey,basez,*self.pos,times)
	def direction_of_attached_line(self,reration):
		"""
		`reration` is this square and target foldline's differ of position or its initial reration(char).
		however,when element isn't 0,it's always regarded as 1.
		"""
		if isinstance(reration,tuple):
			return tuple(int(d == 0 and r == 0) for d,r in zip(self.direction,reration))#(1,1,1)-direction-reration_vector
		elif isinstance(reration, str):
			return self.direction_of_attached_line(self.differ_to(reration))
	def __str__(self):
		return self.mode
class Foldline:
	def __init__(self,posx:int,posy:int,posz:int,direction:str,mode:str,identity:int):
		"""
		pos is middle of the line\n
		direction is one of basis vectors\n
		mode is one of "R","r","0","f","F"\n
		identity is to identify this instance on Origami
		"""
		self.identity=identity
		self.pos=posx,posy,posz
		self.direction=tuple(map(abs,direction_str_cast_to_vector(direction)))#positivate
		self.executed=False
		self.outside_level=0
		self.next_to={"t":None,"b":None,"l":None,"r":None}
		if not mode in "Rr0fF":
			raise ValueError("mode must be char:one of \"Rr0fF\",not {}".format(mode))
		self.mode=mode
	def rotate(self,axis,basex,basey,basez,times=1):
		if self.executed is True:
			warnings.warn("excuted Foldline was rotated")
		self.direction = tuple(map(abs,perpendicular_rotate(axis,0,0,0,*self.direction,times)))
		self.pos = perpendicular_rotate(axis,basex,basey,basez,*self.pos,times)
	def __str__(self):
		return self.mode
class Vertex:
	def __init__(self,identity:int):
		"""
		vertex is just marker\n
		identity is to identify this instance on Origami
		"""
		self.identity=identity
		self.next_to={"t":None,"b":None,"l":None,"r":None}
	def __str__(self):
		return "p"
class Origami:
	def __init__(self,
		squares="0000000000000000",
		ver_foldlines="000000000000",
		hor_foldlines="000000000000",
		hor_size=4,ver_size=4):
		"""
		ABOUT STRUCTURE:\n
		compose structure like,
		```
		--- hor|hor|hor|hor
		ver sqr|sqr|sqr|sqr
		--- --- --- --- ---
		ver sqr|sqr|sqr|sqr
		--- --- --- --- ---
		ver sqr|sqr|sqr|sqr
		```
		(in case that hor_size=4,ver_size=3)
		ver_foldline is |\n
		hor_foldline is ---\n
		at initial situation,all objects are in Origin but for self.sequares[0]\n
		only self.sequares[0] has positional and directional information:pos(0.5,0.5,0),direction(0,0,-1),headway(0,1,0)\n
		when you designate arguments,imagine a piece of paper which is on xy-plane. 
		:::::::::::::::::::::::::::::\n
		ABOUT ARGMENT:\n
		arg:squares is a string of mode of Square.\n
		the first char means bottom-left square's mode,the last one means top-right square's.\n
		in other words,the mode is applied to the square which is in left-most(amap) on bottom-most(amap) line.\n
		square:mode = one of Rr0fF\n
		for detail,refer to 'Datastructure2.png'.\n
		\n
		arg:ver_foldlines and arg:hor_foldlines are strings of mode of Foldline\n
		the order is as well as that of squares.(see the line 6-lines before)\n
		Foldline:mode = one of Rr0fF\n
		for detail,refer to 'Datastructure2.png'.\n
		::::::::::::::::::::::::::::::::
		ABOUT ID and SPECIFICATION:\n
		Square(0.5,0.5,0) and Foldline(0.5,0,0) will never move.\n
		each squares' identitiy is the same with its index on self.squares\n
		each hor_foldlines' identitiy is 1 + 10*(its index on self.hor_foldline)\n
		each ver_foldlines' identitiy is 0 + 10*(its index on self.ver_foldline)\n
		each vertexes' indentity is its index on self.vertexes\n
		"""
		self.executed=False#is position fixed?
		self.consistent=None#is consistent?None:Unchecked
		self.cuberange=None#is in cuberange?
		#cuberange is squares in the same plane have the same position
		#And the square cross at right angle and connect with all other squares
		#which are in the planes which are cross right angle with the plane the square is in.
		self.cubeable=None

		self.center_of_cubelike_structure=None
		self.size=hor_size,ver_size
		self.length = hor_size*ver_size
		#:::::structure initilize
		self.squares=[]#ready
		for y in range(self.size[1]):
			for x in range(self.size[0]):
				self.squares.append(Square(
					0,0,0,(0,0,0),(0,0,0),
					squares[self.square_index(x,y)],
					self.square_index(x,y)
					)
				)
		self.ver_foldlines=[]#ready
		for y in range(self.size[1]):
			for x in range(self.size[0]-1):
				self.ver_foldlines.append(Foldline(
					0,0,0,(0,0,0),
					ver_foldlines[self.ver_foldline_index(x,y)],
					10*self.ver_foldline_index(x,y)
					)
				)
		self.hor_foldlines=[]#ready
		for y in range(self.size[1]-1):
			for x in range(self.size[0]):
				self.hor_foldlines.append(Foldline(
					0,0,0,(0,0,0),
					hor_foldlines[self.hor_foldline_index(x,y)],
					10*self.hor_foldline_index(x,y)+1
					)
				)
		self.vertexes=[]#ready
		for y in range(self.size[1]-1):
			for x in range(self.size[0]-1):
				self.vertexes.append(Vertex(
					self.vertex_index(x,y)
					)
				)
		#set initial position
		self.squares[0].pos=0.5,0.5,0
		self.squares[0].direction=(0,0,-1)
		self.squares[0].headway=(0,1,0)
		self.squares[0].executed=True
		self.squares[0].fixed_side="b"
  		#:::::setting next_to attribute
		for i,s in enumerate(self.squares):
			#is there top side object for the Square? if no,top side isn't registered.
			if not self.length-self.size[0]<=i<self.length:
				s.next_to["t"]=self.hor_foldlines[i]
				self.hor_foldlines[i].next_to["b"]=s
			#bottom side of the square
			if not 0<=i<self.size[0]:
				s.next_to["b"]=self.hor_foldlines[i-self.size[0]]
				self.hor_foldlines[i-self.size[0]].next_to["t"]=s
			#left side of the square
			if not i%self.size[0]==0:
				s.next_to["l"]=self.ver_foldlines[i-(i//self.size[0])-1]
				self.ver_foldlines[i-(i//self.size[0])-1].next_to["r"]=s
			#right side of the square
			if not i%self.size[0]==self.size[0]-1:
				s.next_to["r"]=self.ver_foldlines[i-(i//self.size[0])]
				self.ver_foldlines[i-(i//self.size[0])].next_to["l"]=s
		for i,v in enumerate(self.vertexes):
			#top side of the vertex
			v.next_to["t"]=self.ver_foldlines[i+self.size[0]-1]
			self.ver_foldlines[i+self.size[0]-1].next_to["b"]=v
			#bottom side of the vertex
			v.next_to["b"]=self.ver_foldlines[i]
			self.ver_foldlines[i].next_to["t"]=v
			#left side of the vertex
			v.next_to["l"]=self.hor_foldlines[i+(i//(self.size[0]-1))]
			self.hor_foldlines[i+(i//(self.size[0]-1))].next_to["r"]=v
			#right side of the vertex
			v.next_to["r"]=self.hor_foldlines[i+1+(i//(self.size[0]-1))]
			self.hor_foldlines[i+1+(i//(self.size[0]-1))].next_to["l"]=v
	def square_index(self,x,y)->int:
		if 0>x or 0>y or x>=self.size[0] or y>=self.size[1]:
			warnings.warn("out of range.{},{} is not within {},{}".format(x,y,self.size[0]-1,self.size[1]-1))
			return None
		return x+(self.size[0])*y
	def square_2dindex(self,e)->tuple:
		if 0>e or e>=self.length:
			warnings.warn("out of range.{} is not within {}".format(e,self.length-1))
			return None
		return e%self.size[0],e//self.size[0]
	def ver_foldline_index(self,x,y)->int:
		if 0>x or 0>y or x>=self.size[0]-1 or y>=self.size[1]:
			warnings.warn("out of range.{},{} is not within {},{}".format(x,y,self.size[0]-2,self.size[1]-1))
			return None
		return x+(self.size[0]-1)*y
	def ver_foldline_2dindex(self,e)->tuple:
		if 0>e or e>=self.length-self.size[1]:
			warnings.warn("out of range.{} is not within {}".format(e,self.length-self.size[1]-1))
			return None
		return e%(self.size[0]-1),e//(self.size[0]-1)
	def hor_foldline_index(self,x,y)->int:
		if 0>x or 0>y or x>=self.size[0] or y>=self.size[1]-1:
			warnings.warn("out of range.{},{} is not within {},{}".format(x,y,self.size[0]-1,self.size[1]-2))
			return None
		return x+(self.size[0])*y
	def hor_foldline_2dindex(self,e)->tuple:
		if 0>e or e>=self.length-self.size[0]:
			warnings.warn("out of range.{} is not within {}".format(e,self.length-self.size[1]-1))
			return None
		return e%self.size[0],e//self.size[0]
	def vertex_index(self,x,y)->int:
		if 0>x or 0>y or x>=self.size[0]-1 or y>=self.size[1]-1:
			warnings.warn("out of range.{},{} is not within {},{}".format(x,y,self.size[0]-2,self.size[1]-2))
			return None
		return x+(self.size[0]-1)*y
	def vertex_2dindex(self,e)->tuple:
		if 0>e or e>=self.length-self.size[0]-self.size[1]+1:
			warnings.warn("out of range.{} is not within {}".format(e,self.length-self.size[1]-self.size[1]))
			return None
		return e%(self.size[0]-1),e//(self.size[0]-1)
	def __str__(self):
		cur = self.squares[0]
		left_most = []
		while not cur is None:
			left_most.append(cur)
			cur = cur.next_to["t"]
		res =  ""
		for cur in left_most[::-1]:
			line = ""
			while not cur is None:
				line += str(cur)
				cur = cur.next_to["r"]
			res += line + "\n"
		return res[:-1]
	def cast_foldline_mode_to_rotation_times(self,base_square,middle_line,target_square):
		"""From two squares(have same rotation) and the foldline between them,return proper rotation times.
		For detail,refer to 'foldline rotation direction.png'"""
		primitive = {"F":-2,"f":-1,"0":0,"r":1,"R":2}[middle_line.mode]
		times_at_r_mode_and_positive_position=ROTATION_TIMES_AT_r_AND_POSITIVE_POSITION_TABLE\
		[middle_line.direction][target_square.direction]#tuple(map(abs,base_square.direction))
		#when r mode provide positive rotation on pv<0,this return -1 to reform
		#from ((.pos - base_square.pos)*direction_sign) to 1 for positive rotation.
		positional_sign=sum(target_square.pos)-sum(base_square.pos)
		return positional_sign*times_at_r_mode_and_positive_position*primitive#*direction_sign
	def extend_executed(self,square_identity:int,way:str):
		"""this extend excuted square and foldline\n
		square_identity is index which can match to its attribute:identity\n
		immobile_side expect one of chars:'tbrl'\n
		way is either r or t"""
		base = self.squares[square_identity]
		differ = base.differ_to(way)
		#setting foldline
		middle_line=base.next_to[way]
		if middle_line is None:
			return None
		middle_line.pos = tuple(map(lambda b,r:b+(r*0.5),base.pos,differ))
		middle_line.direction = base.direction_of_attached_line(differ)
		middle_line.outside_level = base.outside_level
		#setting square
		next_square = middle_line.next_to[way]
		next_square.pos = tuple(map(lambda b,n:b+n,base.pos,differ))
		next_square.direction=base.direction_of_square_on(way)
		next_square.headway=base.headway_of_square_on(way)
		next_square.fixed_side={"r":"l","l":"r","b":"t","t":"b"}[way]
		next_square.outside_level = base.outside_level
		#rotate square
		next_square.outside_level += {"F":-1.0,"R":1.0}.get(middle_line.mode,0.0)*sum(next_square.direction)
		middle_line.outside_level = (next_square.outside_level + middle_line.outside_level)/2
		next_square.rotate(
			middle_line.direction,*middle_line.pos,
			self.cast_foldline_mode_to_rotation_times(base,middle_line,next_square)
		)
		next_square.executed=True
		middle_line.executed=True
		return next_square.identity
	def fold_all(self):####
		"""
		make all square executed
		"""
		#extend executed to all squares from [0]
		if not self.executed:
			cursor=0
			cursor2=0
			while not cursor is None:
				while not cursor2 is None:
					cursor2 = self.extend_executed(cursor2,"t")
				cursor = self.extend_executed(cursor,"r")
				cursor2 = cursor
			self.executed = True
			return self.executed
		else:
			warnings.warn("the request was ignored.this Origami has already been executed.")
			return self.executed
	def fold_all_shadow(self):
		if not self.executed:
			cursor=0
			cursor2=0
			while not cursor is None:
				while not cursor2 is None:
					cursor2 = self.extend_executed(cursor2,"r")
				cursor = self.extend_executed(cursor,"t")
				cursor2 = cursor
			self.executed=True
			return self.executed
		else:
			warnings.warn("the request was ignored.this Origami has already been executed.")
			return self.executed
	def check_consistency_of_foldline(self):####
		"""
		make all rests of the foldlines executed after fold_all
		"""
		if self.consistent is None:
			#for f in self.hor_foldlines: all of self.hor_foldlines should be executed in fold_all
			#In order to check consistency,this check two squares which are put next to the foldline
			#shows the same foldline status 
			if not self.executed:
				self.fold_all()
			for f in self.ver_foldlines:
				#position check
				if f.executed:
					continue
				ls=f.next_to["l"]
				f.direction=ls.direction_of_attached_line("r")
				f.pos=tuple(map(lambda b,r:b+(r*0.5),ls.pos,ls.differ_to("r")))
				rs=f.next_to["r"]

				if (
					f.direction!=rs.direction_of_attached_line("l") or 
					f.pos!=tuple(map(lambda b,l:b+(l*0.5),rs.pos,rs.differ_to("l")))
				):
					self.consistent=False
					return False
				else:
					f.executed=True
			
			shadow = Origami(
				"".join(s.mode for s in self.squares),
				"".join(f.mode for f in self.ver_foldlines),
				"".join(f.mode for f in self.hor_foldlines)
				,self.size[0],self.size[1]
			)
			if not shadow.fold_all_shadow():#fold all shadow is executed here
				self.consistent=False
				return False
			for s,o in zip(shadow.squares,self.squares):
				if (
					s.pos != o.pos
				) or (
					s.mode == "0" and s.direction!=o.direction
				) or (
					s.mode != "0" and tuple(map(abs,s.direction))!=tuple(map(abs,o.direction))
				):
					self.consistent=False
					return False
			self.consistent=True
			return True
		else:
			warnings.warn("the request was ignored.consistency of this origami has already been checked.")
			return self.consistent
	def check_cuberange(self):
		#cuberange is squares in the same plane have the same position
		#And the square cross at right angle and connect with all other squares
		#which are in the planes which are cross right angle with the plane the square is in.
		if self.cuberange is None:
			if self.consistent is None:
				self.check_consistency_of_foldline()
			if not self.consistent:
				self.cuberange=False
				return False
			plane={}
			for s in self.squares:
				#s.pos*abs(s.direction)->the plane square is in.
				#self.squares[0] is in plane:[(0,0,1)][0]
				p_size=sum(map(lambda p,d:p*abs(d),s.pos,s.direction))
				p_dire=tuple(map(abs,s.direction))
				if p_dire in plane and p_size in plane[p_dire]:
					if plane[p_dire][p_size]!=s.pos:
						self.cuberange=False
						return False
				else:
					if not p_dire in plane:
						plane[p_dire]={}
					plane[p_dire][p_size]=s.pos
			how_far=lambda bp,tp:float(str(((bp[0]-tp[0])**2+(bp[1]-tp[1])**2+(bp[2]-tp[2])**2)**0.5)[:10])
			#to take the ten upper digtis in order to measures against rounding error
			for bp in plane.get((0,0,1),{}).values():
				for tp in (*plane.get((0,1,0),{}).values(),*plane.get((1,0,0),{}).values()):
					if how_far(bp,tp)!=MODEL_DISTANCE["r"]:
						self.cuberange=False
						return False
			for bp in plane.get((0,1,0),{}).values():
				for tp in (*plane.get((0,0,1),{}).values(),*plane.get((1,0,0),{}).values()):
					if how_far(bp,tp)!=MODEL_DISTANCE["r"]:
						self.cuberange=False
						return False
			for bp in plane.get((1,0,0),{}).values():
				for tp in (*plane.get((0,1,0),{}).values(),*plane.get((0,0,1),{}).values()):
					if how_far(bp,tp)!=MODEL_DISTANCE["r"]:
						self.cuberange=False
						return False
			self.cuberange=True
			return True
		else:
			warnings.warn("the request was ignored.cuberangeablity of this origami has already been checked.")
			return self.cuberange
	def debag_print(self):
		print(self.check_consistency_of_foldline())
		print(self.check_cuberange())
		print(self.visualize())
	def visualize(self):
		"""this return the status of instance in the easy way to see.\n
			format is [mode(posision)(direcyion)]
		"""
		rows=[]
		sub_cursor=self.squares[0]
		cursor=sub_cursor
		while not sub_cursor is None:
			row=[]
			maxlen=0
			while not cursor is None:
				if isinstance(cursor,Vertex):
					string="[---]"
				else:
					string="["+str(cursor.mode)+str(cursor.pos)+str(cursor.direction)+str(cursor.outside_level)+"]"
				maxlen=max(len(string),maxlen)
				row.append(string)
				cursor=cursor.next_to["t"]
			rows.append([string + " "*(maxlen-len(string)) for string in row[::-1]])
			sub_cursor=sub_cursor.next_to["r"]
			cursor=sub_cursor
		lines=[]
		for i in range(len(rows[0])):
			lines.append(" ".join([row[i] for row in rows]))
		return "\n".join(lines)

def test():
	Origami("0R0f0R00000Rfr0F","rfRrfffffRFf","rFffFFfFfffR").debag_print()#cubable
	Origami("0R0f0R00000Rfr0F","rfRrfffffRFf","rFffRRfRfffR").debag_print()#inconsist
	Origami("000000000000000R","000000000000","0000frRF0000").debag_print()#inconsist
	Origami("R000000000000000","r00r00r00r00","Frrr00000000").debag_print()#consist
	Origami("0r00","Rf","ff",2,2).debag_print()#cuberange
	Origami("0r00","rf","f0",2,2).debag_print()#consist
	Origami("0r00","RF","ff",2,2).debag_print()#inconsist
	"""cubable_example1.debug_print()
	#excepted output
	#rRFF0fR
	#fpfpfpR
	#0f0f0fF
	#FpFpfpF
	#0rFf0f0
	#rpFpfpf
	#0rFf0Rr
	print(cubable_example1)"""#initilizer:works all green.
	"""known bugs:
	Foldline mode:"FR" can't be distinguished
	"""
test()
def _3_3_cuberange_patterns():#it's estimated to take 1388 days to finish.
	cubable=[]
	for si,s in enumerate(itertools.product("RFrf0",repeat=9)):#5**9*
		for vi,v in enumerate(itertools.product("Rrf",repeat=6)):#3**6*
			for hi,h in enumerate(itertools.product("Rrf",repeat=6)):#3**6=1037970703125
				print("progress {}/{}".format(si*3**12+vi*3**6+hi,1037970703125))
				ori=Origami("".join(s),"".join(v),"".join(h),3,3)
				if ori.check_cuberange():
					cubable.append((s,v,h))
	return cubable
#print(_3_3_cuberange_patterns())