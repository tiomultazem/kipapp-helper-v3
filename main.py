J=enumerate
I=bytes
F=open
D=print
def A(a,b):return I(B^b+A*31&255 for(A,B)in J(a)).decode()
import sys as E,os as B,importlib as K,base64 as L,json as G,re,shutil as M,stat as C,zlib
def N():from frames import PACKAGE_ACCENT as C;from frames.entriFrame import ENTRI_ACCENT as D;from frames.rkFrame import RK_ACCENT as E;from frames.skpFrame import SKP_ACCENT as F;from frames.taskFrame import TASK_ACCENT as G;from frames.update import UPDATE_ACCENT as B;H=C[0],D[0],E[0],F[0],G[0],C[1],B[0],B[1],B[2],B[3],B[4],B[2],B[5],B[6];return''.join(H).encode(A((97,71,52,92,168),20))
def O(data):C=G.dumps(data,ensure_ascii=False,separators=(A((119,),91),A((188,),134))).encode(A((30,254,207,229,223),107));B=N();D=I(C^B[A%len(B)]for(A,C)in J(C));return L.urlsafe_b64encode(zlib.compress(D,9)).decode(A((188,143,120,83,48),221))
def P(base_dir):
	E=base_dir;D=B.path.join(E,A((227,214,162,143,100,83),133),A((29,235,202,247,136,110),124));H=B.path.join(E,A((252,214,179,134,122,93,61,6,226,158,165,157,98,66),153))
	if not B.path.exists(D)or not B.path.exists(H):return
	with F(H,A((3,),113),encoding=A((162,130,115,25,107,95,226,217,168),215))as C:K=G.load(C)
	L=O(K)
	with F(D,A((217,),171),encoding=A((45,3,240,152,236),88))as C:I=C.read()
	M=A((183,32,116,3,36,200,230,134,190,69,81,122,13,51,210,244,141,171,75,69,127,73,207,193,251,217,45,117,12,65,209,203,228,146,55,11,124,59,223,143,252,189,213,60),233);J,N=re.subn(M,f'\\1"{L}"',I,count=1,flags=re.MULTILINE)
	if N==0:raise RuntimeError(A((88,111,8,36,194,226,154,161,77,102,17,47,54,208,233,143,219,110,80,60,22,253,149,176,154,102,84,61,26,229,204,162,203,110,64,104,1,244,196,169,134,113,14,33,47,14,179,204,162),11))
	if J!=I:
		with F(D,A((94,),41),encoding=A((185,159,108,4,112),204))as C:C.write(J)
def Q(func,path,_exc_info):A=path;B.chmod(A,B.stat(A).st_mode|C.S_IWRITE);func(A)
def H(*F):
	D=B.path.dirname(B.path.abspath(__file__));E=B.path.realpath(D)
	for G in F:
		A=B.path.realpath(B.path.join(D,G))
		if A==E or not A.startswith(E+B.sep):continue
		try:
			if B.path.isdir(A):M.rmtree(A,onerror=Q)
			elif B.path.isfile(A):B.chmod(A,B.stat(A).st_mode|C.S_IWRITE);B.remove(A)
		except OSError:pass
def R():
	F={A((17,228,195,187,129,96,88,32,3,231,220,162,148),114):A((107,82,53,17,235,206,182,138,105,113,74,56,14),8),A((98,74,63,24,233,216,190,154),16):A((211,165,174,139,120,79,47,9),161),A((95,63,11,227,220,178,146,101),48):A((174,144,154,112,77,37,3,246),193),A((83,57,1,241,221,164),55):A((82,56,20,23,241,211,241,159,117,77,61,25,224),34),A((242,220,250),144):A((207,169,138,127,93,33,1,243,201,183,140,119,81,116),173)};B=[]
	for(G,H)in F.items():
		try:__import__(G)
		except ImportError:B.append(H)
	if B:import subprocess as C;D(f"Menginstal dependensi: {A((92,175),112).join(B)}...");C.check_call([E.executable,A((246,151),219),A((205,181,139),189),A((191,155,103,71,51,29,252),214),*B,A((22,43),59)],stdout=C.DEVNULL);D(A((9,9,251,207,167,140,98,72,54,13,163,214,164,146,150,112,78,40,26,246,151),77))
def S():
	H(A((185,117,86,42,20,224,212,218,241),230));R();G=E.version_info.minor;C=B.path.dirname(B.path.abspath(__file__))
	if B.path.isdir(B.path.join(C,A((166,173,159,112,89,40),192))):P(C);F=A((187,142,122,87,60,11),221)
	else:
		H(A((47,15,167,216,190),75));F=f"frames{G}"
		if not B.path.isdir(B.path.join(C,F)):
			I=sorted([f"3.{D[6:]}"for D in B.listdir(C)if B.path.isdir(B.path.join(C,D))and D.startswith(A((122,73,59,20,253,196),28))and D[6:].isdigit()]);D(f"Python 3.{G} tidak didukung.")
			if I:D(f"   Versi yang tersedia: {A((152,243),180).join(I)}")
			E.exit(1)
	J=K.import_module(f"{F}.gui");L=J.Gui();L.mainloop()
if __name__==A((127,96,51,28,245,213,133,166),32):S()
