                              1 ;--------------------------------------------------------
                              2 ; File Created by SDCC : free open source ANSI-C Compiler
                              3 ; Version 3.6.8 #9946 (Linux)
                              4 ;--------------------------------------------------------
                              5 	.module building_2
                              6 	.optsdcc -mz80
                              7 	
                              8 ;--------------------------------------------------------
                              9 ; Public variables in this module
                             10 ;--------------------------------------------------------
                             11 	.globl _g_building_2
                             12 ;--------------------------------------------------------
                             13 ; special function registers
                             14 ;--------------------------------------------------------
                             15 ;--------------------------------------------------------
                             16 ; ram data
                             17 ;--------------------------------------------------------
                             18 	.area _DATA
                             19 ;--------------------------------------------------------
                             20 ; ram data
                             21 ;--------------------------------------------------------
                             22 	.area _INITIALIZED
                             23 ;--------------------------------------------------------
                             24 ; absolute external ram data
                             25 ;--------------------------------------------------------
                             26 	.area _DABS (ABS)
                             27 ;--------------------------------------------------------
                             28 ; global & static initialisations
                             29 ;--------------------------------------------------------
                             30 	.area _HOME
                             31 	.area _GSINIT
                             32 	.area _GSFINAL
                             33 	.area _GSINIT
                             34 ;--------------------------------------------------------
                             35 ; Home
                             36 ;--------------------------------------------------------
                             37 	.area _HOME
                             38 	.area _HOME
                             39 ;--------------------------------------------------------
                             40 ; code
                             41 ;--------------------------------------------------------
                             42 	.area _CODE
                             43 	.area _CODE
   42D0                      44 _g_building_2:
   42D0 FF                   45 	.db #0xff	; 255
   42D1 FF                   46 	.db #0xff	; 255
   42D2 FF                   47 	.db #0xff	; 255
   42D3 FF                   48 	.db #0xff	; 255
   42D4 FF                   49 	.db #0xff	; 255
   42D5 FF                   50 	.db #0xff	; 255
   42D6 FF                   51 	.db #0xff	; 255
   42D7 FF                   52 	.db #0xff	; 255
   42D8 FF                   53 	.db #0xff	; 255
   42D9 FF                   54 	.db #0xff	; 255
   42DA FF                   55 	.db #0xff	; 255
   42DB FF                   56 	.db #0xff	; 255
   42DC FF                   57 	.db #0xff	; 255
   42DD FF                   58 	.db #0xff	; 255
   42DE FF                   59 	.db #0xff	; 255
   42DF FF                   60 	.db #0xff	; 255
   42E0 FF                   61 	.db #0xff	; 255
   42E1 FF                   62 	.db #0xff	; 255
   42E2 FF                   63 	.db #0xff	; 255
   42E3 FF                   64 	.db #0xff	; 255
   42E4 FF                   65 	.db #0xff	; 255
   42E5 FF                   66 	.db #0xff	; 255
   42E6 FF                   67 	.db #0xff	; 255
   42E7 FF                   68 	.db #0xff	; 255
   42E8 FF                   69 	.db #0xff	; 255
   42E9 FF                   70 	.db #0xff	; 255
   42EA FF                   71 	.db #0xff	; 255
   42EB FF                   72 	.db #0xff	; 255
   42EC FF                   73 	.db #0xff	; 255
   42ED FB                   74 	.db #0xfb	; 251
   42EE F7                   75 	.db #0xf7	; 247
   42EF FF                   76 	.db #0xff	; 255
   42F0 BB                   77 	.db #0xbb	; 187
   42F1 77                   78 	.db #0x77	; 119	'w'
   42F2 FF                   79 	.db #0xff	; 255
   42F3 FF                   80 	.db #0xff	; 255
   42F4 FB                   81 	.db #0xfb	; 251
   42F5 F7                   82 	.db #0xf7	; 247
   42F6 FF                   83 	.db #0xff	; 255
   42F7 BB                   84 	.db #0xbb	; 187
   42F8 77                   85 	.db #0x77	; 119	'w'
   42F9 FF                   86 	.db #0xff	; 255
   42FA FF                   87 	.db #0xff	; 255
   42FB FF                   88 	.db #0xff	; 255
   42FC FF                   89 	.db #0xff	; 255
   42FD FF                   90 	.db #0xff	; 255
   42FE FF                   91 	.db #0xff	; 255
   42FF FF                   92 	.db #0xff	; 255
   4300 FF                   93 	.db #0xff	; 255
   4301 FF                   94 	.db #0xff	; 255
   4302 FF                   95 	.db #0xff	; 255
   4303 FF                   96 	.db #0xff	; 255
   4304 FF                   97 	.db #0xff	; 255
   4305 FF                   98 	.db #0xff	; 255
   4306 FF                   99 	.db #0xff	; 255
   4307 FF                  100 	.db #0xff	; 255
   4308 FF                  101 	.db #0xff	; 255
   4309 FF                  102 	.db #0xff	; 255
   430A FF                  103 	.db #0xff	; 255
   430B FF                  104 	.db #0xff	; 255
   430C FF                  105 	.db #0xff	; 255
   430D FF                  106 	.db #0xff	; 255
   430E FF                  107 	.db #0xff	; 255
   430F FF                  108 	.db #0xff	; 255
   4310 FF                  109 	.db #0xff	; 255
   4311 FF                  110 	.db #0xff	; 255
   4312 FF                  111 	.db #0xff	; 255
   4313 FF                  112 	.db #0xff	; 255
   4314 FF                  113 	.db #0xff	; 255
   4315 FF                  114 	.db #0xff	; 255
   4316 FF                  115 	.db #0xff	; 255
   4317 AB                  116 	.db #0xab	; 171
   4318 57                  117 	.db #0x57	; 87	'W'
   4319 FF                  118 	.db #0xff	; 255
   431A FB                  119 	.db #0xfb	; 251
   431B F7                  120 	.db #0xf7	; 247
   431C FF                  121 	.db #0xff	; 255
   431D FF                  122 	.db #0xff	; 255
   431E AB                  123 	.db #0xab	; 171
   431F 57                  124 	.db #0x57	; 87	'W'
   4320 FF                  125 	.db #0xff	; 255
   4321 FB                  126 	.db #0xfb	; 251
   4322 F7                  127 	.db #0xf7	; 247
   4323 FF                  128 	.db #0xff	; 255
   4324 FF                  129 	.db #0xff	; 255
   4325 FF                  130 	.db #0xff	; 255
   4326 FF                  131 	.db #0xff	; 255
   4327 FF                  132 	.db #0xff	; 255
   4328 FF                  133 	.db #0xff	; 255
   4329 FF                  134 	.db #0xff	; 255
   432A FF                  135 	.db #0xff	; 255
   432B FF                  136 	.db #0xff	; 255
   432C FF                  137 	.db #0xff	; 255
   432D FF                  138 	.db #0xff	; 255
   432E FF                  139 	.db #0xff	; 255
   432F FF                  140 	.db #0xff	; 255
   4330 FF                  141 	.db #0xff	; 255
   4331 FF                  142 	.db #0xff	; 255
   4332 FF                  143 	.db #0xff	; 255
   4333 FF                  144 	.db #0xff	; 255
   4334 FF                  145 	.db #0xff	; 255
   4335 FF                  146 	.db #0xff	; 255
   4336 FF                  147 	.db #0xff	; 255
   4337 FF                  148 	.db #0xff	; 255
   4338 FF                  149 	.db #0xff	; 255
   4339 FF                  150 	.db #0xff	; 255
   433A FF                  151 	.db #0xff	; 255
   433B FF                  152 	.db #0xff	; 255
   433C FF                  153 	.db #0xff	; 255
   433D FF                  154 	.db #0xff	; 255
   433E FF                  155 	.db #0xff	; 255
   433F FF                  156 	.db #0xff	; 255
   4340 FF                  157 	.db #0xff	; 255
   4341 FB                  158 	.db #0xfb	; 251
   4342 F7                  159 	.db #0xf7	; 247
   4343 FF                  160 	.db #0xff	; 255
   4344 FB                  161 	.db #0xfb	; 251
   4345 F7                  162 	.db #0xf7	; 247
   4346 FF                  163 	.db #0xff	; 255
   4347 FF                  164 	.db #0xff	; 255
   4348 FB                  165 	.db #0xfb	; 251
   4349 F7                  166 	.db #0xf7	; 247
   434A FF                  167 	.db #0xff	; 255
   434B FB                  168 	.db #0xfb	; 251
   434C F7                  169 	.db #0xf7	; 247
   434D FF                  170 	.db #0xff	; 255
   434E FF                  171 	.db #0xff	; 255
   434F FF                  172 	.db #0xff	; 255
   4350 FF                  173 	.db #0xff	; 255
   4351 FF                  174 	.db #0xff	; 255
   4352 FF                  175 	.db #0xff	; 255
   4353 FF                  176 	.db #0xff	; 255
   4354 FF                  177 	.db #0xff	; 255
   4355 FF                  178 	.db #0xff	; 255
   4356 FF                  179 	.db #0xff	; 255
   4357 FF                  180 	.db #0xff	; 255
   4358 FF                  181 	.db #0xff	; 255
   4359 FF                  182 	.db #0xff	; 255
   435A FF                  183 	.db #0xff	; 255
   435B FF                  184 	.db #0xff	; 255
   435C FF                  185 	.db #0xff	; 255
   435D FF                  186 	.db #0xff	; 255
   435E FF                  187 	.db #0xff	; 255
   435F FF                  188 	.db #0xff	; 255
   4360 FF                  189 	.db #0xff	; 255
   4361 FF                  190 	.db #0xff	; 255
   4362 FF                  191 	.db #0xff	; 255
   4363 FF                  192 	.db #0xff	; 255
   4364 FF                  193 	.db #0xff	; 255
   4365 FF                  194 	.db #0xff	; 255
   4366 FF                  195 	.db #0xff	; 255
   4367 FF                  196 	.db #0xff	; 255
   4368 FF                  197 	.db #0xff	; 255
   4369 FF                  198 	.db #0xff	; 255
   436A FF                  199 	.db #0xff	; 255
   436B FB                  200 	.db #0xfb	; 251
   436C F7                  201 	.db #0xf7	; 247
   436D FF                  202 	.db #0xff	; 255
   436E BB                  203 	.db #0xbb	; 187
   436F 77                  204 	.db #0x77	; 119	'w'
   4370 FF                  205 	.db #0xff	; 255
   4371 FF                  206 	.db #0xff	; 255
   4372 FB                  207 	.db #0xfb	; 251
   4373 F7                  208 	.db #0xf7	; 247
   4374 FF                  209 	.db #0xff	; 255
   4375 BB                  210 	.db #0xbb	; 187
   4376 77                  211 	.db #0x77	; 119	'w'
   4377 FF                  212 	.db #0xff	; 255
   4378 FF                  213 	.db #0xff	; 255
   4379 FF                  214 	.db #0xff	; 255
   437A FF                  215 	.db #0xff	; 255
   437B FF                  216 	.db #0xff	; 255
   437C FF                  217 	.db #0xff	; 255
   437D FF                  218 	.db #0xff	; 255
   437E FF                  219 	.db #0xff	; 255
   437F FF                  220 	.db #0xff	; 255
   4380 FF                  221 	.db #0xff	; 255
   4381 FF                  222 	.db #0xff	; 255
   4382 FF                  223 	.db #0xff	; 255
   4383 FF                  224 	.db #0xff	; 255
   4384 FF                  225 	.db #0xff	; 255
   4385 FF                  226 	.db #0xff	; 255
   4386 FF                  227 	.db #0xff	; 255
   4387 FF                  228 	.db #0xff	; 255
   4388 FF                  229 	.db #0xff	; 255
   4389 FF                  230 	.db #0xff	; 255
   438A FF                  231 	.db #0xff	; 255
   438B FF                  232 	.db #0xff	; 255
   438C FF                  233 	.db #0xff	; 255
   438D FF                  234 	.db #0xff	; 255
   438E FF                  235 	.db #0xff	; 255
   438F FF                  236 	.db #0xff	; 255
   4390 FF                  237 	.db #0xff	; 255
   4391 FF                  238 	.db #0xff	; 255
   4392 FF                  239 	.db #0xff	; 255
   4393 FF                  240 	.db #0xff	; 255
   4394 FF                  241 	.db #0xff	; 255
   4395 AB                  242 	.db #0xab	; 171
   4396 57                  243 	.db #0x57	; 87	'W'
   4397 FF                  244 	.db #0xff	; 255
   4398 FB                  245 	.db #0xfb	; 251
   4399 F7                  246 	.db #0xf7	; 247
   439A FF                  247 	.db #0xff	; 255
   439B FF                  248 	.db #0xff	; 255
   439C AB                  249 	.db #0xab	; 171
   439D 57                  250 	.db #0x57	; 87	'W'
   439E FF                  251 	.db #0xff	; 255
   439F FB                  252 	.db #0xfb	; 251
   43A0 F7                  253 	.db #0xf7	; 247
   43A1 FF                  254 	.db #0xff	; 255
   43A2 FF                  255 	.db #0xff	; 255
   43A3 FF                  256 	.db #0xff	; 255
   43A4 FF                  257 	.db #0xff	; 255
   43A5 FF                  258 	.db #0xff	; 255
   43A6 FF                  259 	.db #0xff	; 255
   43A7 FF                  260 	.db #0xff	; 255
   43A8 FF                  261 	.db #0xff	; 255
   43A9 FF                  262 	.db #0xff	; 255
   43AA FF                  263 	.db #0xff	; 255
   43AB FF                  264 	.db #0xff	; 255
   43AC FF                  265 	.db #0xff	; 255
   43AD FF                  266 	.db #0xff	; 255
   43AE FF                  267 	.db #0xff	; 255
   43AF FF                  268 	.db #0xff	; 255
   43B0 FF                  269 	.db #0xff	; 255
   43B1 FF                  270 	.db #0xff	; 255
   43B2 FF                  271 	.db #0xff	; 255
   43B3 FF                  272 	.db #0xff	; 255
   43B4 FF                  273 	.db #0xff	; 255
   43B5 FF                  274 	.db #0xff	; 255
   43B6 FF                  275 	.db #0xff	; 255
   43B7 FF                  276 	.db #0xff	; 255
   43B8 FF                  277 	.db #0xff	; 255
   43B9 FF                  278 	.db #0xff	; 255
   43BA FF                  279 	.db #0xff	; 255
   43BB FF                  280 	.db #0xff	; 255
   43BC FF                  281 	.db #0xff	; 255
   43BD FF                  282 	.db #0xff	; 255
   43BE FF                  283 	.db #0xff	; 255
   43BF FB                  284 	.db #0xfb	; 251
   43C0 F7                  285 	.db #0xf7	; 247
   43C1 FF                  286 	.db #0xff	; 255
   43C2 FB                  287 	.db #0xfb	; 251
   43C3 F7                  288 	.db #0xf7	; 247
   43C4 FF                  289 	.db #0xff	; 255
   43C5 FF                  290 	.db #0xff	; 255
   43C6 FB                  291 	.db #0xfb	; 251
   43C7 F7                  292 	.db #0xf7	; 247
   43C8 FF                  293 	.db #0xff	; 255
   43C9 FB                  294 	.db #0xfb	; 251
   43CA F7                  295 	.db #0xf7	; 247
   43CB FF                  296 	.db #0xff	; 255
   43CC FF                  297 	.db #0xff	; 255
   43CD FF                  298 	.db #0xff	; 255
   43CE FF                  299 	.db #0xff	; 255
   43CF FF                  300 	.db #0xff	; 255
   43D0 FF                  301 	.db #0xff	; 255
   43D1 FF                  302 	.db #0xff	; 255
   43D2 FF                  303 	.db #0xff	; 255
   43D3 FF                  304 	.db #0xff	; 255
   43D4 FF                  305 	.db #0xff	; 255
   43D5 FF                  306 	.db #0xff	; 255
   43D6 FF                  307 	.db #0xff	; 255
   43D7 FF                  308 	.db #0xff	; 255
   43D8 FF                  309 	.db #0xff	; 255
   43D9 FF                  310 	.db #0xff	; 255
   43DA FF                  311 	.db #0xff	; 255
   43DB FF                  312 	.db #0xff	; 255
   43DC FF                  313 	.db #0xff	; 255
   43DD FF                  314 	.db #0xff	; 255
   43DE FF                  315 	.db #0xff	; 255
   43DF FF                  316 	.db #0xff	; 255
   43E0 FF                  317 	.db #0xff	; 255
   43E1 FF                  318 	.db #0xff	; 255
   43E2 FF                  319 	.db #0xff	; 255
   43E3 FF                  320 	.db #0xff	; 255
   43E4 FF                  321 	.db #0xff	; 255
   43E5 FF                  322 	.db #0xff	; 255
   43E6 FF                  323 	.db #0xff	; 255
   43E7 FF                  324 	.db #0xff	; 255
   43E8 FF                  325 	.db #0xff	; 255
   43E9 FB                  326 	.db #0xfb	; 251
   43EA F7                  327 	.db #0xf7	; 247
   43EB FF                  328 	.db #0xff	; 255
   43EC AB                  329 	.db #0xab	; 171
   43ED 57                  330 	.db #0x57	; 87	'W'
   43EE FF                  331 	.db #0xff	; 255
   43EF FF                  332 	.db #0xff	; 255
   43F0 FB                  333 	.db #0xfb	; 251
   43F1 F7                  334 	.db #0xf7	; 247
   43F2 FF                  335 	.db #0xff	; 255
   43F3 AB                  336 	.db #0xab	; 171
   43F4 57                  337 	.db #0x57	; 87	'W'
   43F5 FF                  338 	.db #0xff	; 255
   43F6 FF                  339 	.db #0xff	; 255
   43F7 FF                  340 	.db #0xff	; 255
   43F8 FF                  341 	.db #0xff	; 255
   43F9 FF                  342 	.db #0xff	; 255
   43FA FF                  343 	.db #0xff	; 255
   43FB FF                  344 	.db #0xff	; 255
   43FC FF                  345 	.db #0xff	; 255
   43FD FF                  346 	.db #0xff	; 255
   43FE FF                  347 	.db #0xff	; 255
   43FF FF                  348 	.db #0xff	; 255
   4400 FF                  349 	.db #0xff	; 255
   4401 FF                  350 	.db #0xff	; 255
   4402 FF                  351 	.db #0xff	; 255
   4403 FF                  352 	.db #0xff	; 255
   4404 FF                  353 	.db #0xff	; 255
   4405 FF                  354 	.db #0xff	; 255
   4406 FF                  355 	.db #0xff	; 255
   4407 FF                  356 	.db #0xff	; 255
   4408 FF                  357 	.db #0xff	; 255
   4409 FF                  358 	.db #0xff	; 255
   440A FF                  359 	.db #0xff	; 255
   440B FF                  360 	.db #0xff	; 255
   440C FF                  361 	.db #0xff	; 255
   440D FF                  362 	.db #0xff	; 255
   440E FF                  363 	.db #0xff	; 255
   440F FF                  364 	.db #0xff	; 255
   4410 FF                  365 	.db #0xff	; 255
   4411 FF                  366 	.db #0xff	; 255
   4412 FF                  367 	.db #0xff	; 255
   4413 BB                  368 	.db #0xbb	; 187
   4414 77                  369 	.db #0x77	; 119	'w'
   4415 FF                  370 	.db #0xff	; 255
   4416 FB                  371 	.db #0xfb	; 251
   4417 F7                  372 	.db #0xf7	; 247
   4418 FF                  373 	.db #0xff	; 255
   4419 FF                  374 	.db #0xff	; 255
   441A BB                  375 	.db #0xbb	; 187
   441B 77                  376 	.db #0x77	; 119	'w'
   441C FF                  377 	.db #0xff	; 255
   441D FB                  378 	.db #0xfb	; 251
   441E F7                  379 	.db #0xf7	; 247
   441F FF                  380 	.db #0xff	; 255
   4420 FF                  381 	.db #0xff	; 255
   4421 FF                  382 	.db #0xff	; 255
   4422 FF                  383 	.db #0xff	; 255
   4423 FF                  384 	.db #0xff	; 255
   4424 FF                  385 	.db #0xff	; 255
   4425 FF                  386 	.db #0xff	; 255
   4426 FF                  387 	.db #0xff	; 255
   4427 FF                  388 	.db #0xff	; 255
   4428 FF                  389 	.db #0xff	; 255
   4429 FF                  390 	.db #0xff	; 255
   442A FF                  391 	.db #0xff	; 255
   442B FF                  392 	.db #0xff	; 255
   442C FF                  393 	.db #0xff	; 255
   442D FF                  394 	.db #0xff	; 255
   442E FF                  395 	.db #0xff	; 255
   442F FF                  396 	.db #0xff	; 255
   4430 FF                  397 	.db #0xff	; 255
   4431 FF                  398 	.db #0xff	; 255
   4432 FF                  399 	.db #0xff	; 255
   4433 FF                  400 	.db #0xff	; 255
   4434 FF                  401 	.db #0xff	; 255
   4435 FF                  402 	.db #0xff	; 255
   4436 FF                  403 	.db #0xff	; 255
   4437 FF                  404 	.db #0xff	; 255
   4438 FF                  405 	.db #0xff	; 255
   4439 FF                  406 	.db #0xff	; 255
   443A FF                  407 	.db #0xff	; 255
   443B FF                  408 	.db #0xff	; 255
   443C FF                  409 	.db #0xff	; 255
   443D FB                  410 	.db #0xfb	; 251
   443E F7                  411 	.db #0xf7	; 247
   443F FF                  412 	.db #0xff	; 255
   4440 BB                  413 	.db #0xbb	; 187
   4441 77                  414 	.db #0x77	; 119	'w'
   4442 FF                  415 	.db #0xff	; 255
   4443 FF                  416 	.db #0xff	; 255
   4444 FB                  417 	.db #0xfb	; 251
   4445 F7                  418 	.db #0xf7	; 247
   4446 FF                  419 	.db #0xff	; 255
   4447 BB                  420 	.db #0xbb	; 187
   4448 77                  421 	.db #0x77	; 119	'w'
   4449 FF                  422 	.db #0xff	; 255
   444A FF                  423 	.db #0xff	; 255
   444B FF                  424 	.db #0xff	; 255
   444C FF                  425 	.db #0xff	; 255
   444D FF                  426 	.db #0xff	; 255
   444E FF                  427 	.db #0xff	; 255
   444F FF                  428 	.db #0xff	; 255
   4450 FF                  429 	.db #0xff	; 255
   4451 FF                  430 	.db #0xff	; 255
   4452 FF                  431 	.db #0xff	; 255
   4453 FF                  432 	.db #0xff	; 255
   4454 FF                  433 	.db #0xff	; 255
   4455 FF                  434 	.db #0xff	; 255
   4456 FF                  435 	.db #0xff	; 255
   4457 FF                  436 	.db #0xff	; 255
   4458 FF                  437 	.db #0xff	; 255
   4459 FF                  438 	.db #0xff	; 255
   445A FF                  439 	.db #0xff	; 255
   445B FF                  440 	.db #0xff	; 255
   445C FF                  441 	.db #0xff	; 255
   445D FF                  442 	.db #0xff	; 255
   445E FF                  443 	.db #0xff	; 255
   445F FF                  444 	.db #0xff	; 255
   4460 FF                  445 	.db #0xff	; 255
   4461 FF                  446 	.db #0xff	; 255
   4462 FF                  447 	.db #0xff	; 255
   4463 FF                  448 	.db #0xff	; 255
   4464 FF                  449 	.db #0xff	; 255
   4465 FF                  450 	.db #0xff	; 255
   4466 FF                  451 	.db #0xff	; 255
   4467 AB                  452 	.db #0xab	; 171
   4468 57                  453 	.db #0x57	; 87	'W'
   4469 FF                  454 	.db #0xff	; 255
   446A FB                  455 	.db #0xfb	; 251
   446B F7                  456 	.db #0xf7	; 247
   446C FF                  457 	.db #0xff	; 255
   446D FF                  458 	.db #0xff	; 255
   446E AB                  459 	.db #0xab	; 171
   446F 57                  460 	.db #0x57	; 87	'W'
   4470 FF                  461 	.db #0xff	; 255
   4471 FB                  462 	.db #0xfb	; 251
   4472 F7                  463 	.db #0xf7	; 247
   4473 FF                  464 	.db #0xff	; 255
   4474 FF                  465 	.db #0xff	; 255
   4475 FF                  466 	.db #0xff	; 255
   4476 FF                  467 	.db #0xff	; 255
   4477 FF                  468 	.db #0xff	; 255
   4478 FF                  469 	.db #0xff	; 255
   4479 FF                  470 	.db #0xff	; 255
   447A FF                  471 	.db #0xff	; 255
   447B FF                  472 	.db #0xff	; 255
   447C FF                  473 	.db #0xff	; 255
   447D FF                  474 	.db #0xff	; 255
   447E FF                  475 	.db #0xff	; 255
   447F FF                  476 	.db #0xff	; 255
   4480 FF                  477 	.db #0xff	; 255
   4481 FF                  478 	.db #0xff	; 255
   4482 FF                  479 	.db #0xff	; 255
   4483 FF                  480 	.db #0xff	; 255
   4484 FF                  481 	.db #0xff	; 255
   4485 FF                  482 	.db #0xff	; 255
   4486 FF                  483 	.db #0xff	; 255
   4487 FF                  484 	.db #0xff	; 255
   4488 FF                  485 	.db #0xff	; 255
   4489 FF                  486 	.db #0xff	; 255
   448A FF                  487 	.db #0xff	; 255
   448B FF                  488 	.db #0xff	; 255
   448C FF                  489 	.db #0xff	; 255
   448D FF                  490 	.db #0xff	; 255
   448E FF                  491 	.db #0xff	; 255
   448F FF                  492 	.db #0xff	; 255
   4490 FF                  493 	.db #0xff	; 255
   4491 FB                  494 	.db #0xfb	; 251
   4492 F7                  495 	.db #0xf7	; 247
   4493 FF                  496 	.db #0xff	; 255
   4494 FB                  497 	.db #0xfb	; 251
   4495 F7                  498 	.db #0xf7	; 247
   4496 FF                  499 	.db #0xff	; 255
   4497 FF                  500 	.db #0xff	; 255
   4498 FB                  501 	.db #0xfb	; 251
   4499 F7                  502 	.db #0xf7	; 247
   449A FF                  503 	.db #0xff	; 255
   449B FB                  504 	.db #0xfb	; 251
   449C F7                  505 	.db #0xf7	; 247
   449D FF                  506 	.db #0xff	; 255
   449E FF                  507 	.db #0xff	; 255
   449F FF                  508 	.db #0xff	; 255
   44A0 FF                  509 	.db #0xff	; 255
   44A1 FF                  510 	.db #0xff	; 255
   44A2 FF                  511 	.db #0xff	; 255
   44A3 FF                  512 	.db #0xff	; 255
   44A4 FF                  513 	.db #0xff	; 255
   44A5 FF                  514 	.db #0xff	; 255
   44A6 FF                  515 	.db #0xff	; 255
   44A7 FF                  516 	.db #0xff	; 255
   44A8 FF                  517 	.db #0xff	; 255
   44A9 FF                  518 	.db #0xff	; 255
   44AA FF                  519 	.db #0xff	; 255
   44AB FF                  520 	.db #0xff	; 255
   44AC FF                  521 	.db #0xff	; 255
   44AD FF                  522 	.db #0xff	; 255
   44AE FF                  523 	.db #0xff	; 255
   44AF FF                  524 	.db #0xff	; 255
   44B0 FF                  525 	.db #0xff	; 255
   44B1 FF                  526 	.db #0xff	; 255
   44B2 FF                  527 	.db #0xff	; 255
   44B3 FF                  528 	.db #0xff	; 255
   44B4 FF                  529 	.db #0xff	; 255
   44B5 FF                  530 	.db #0xff	; 255
   44B6 FF                  531 	.db #0xff	; 255
   44B7 FF                  532 	.db #0xff	; 255
   44B8 FF                  533 	.db #0xff	; 255
   44B9 FF                  534 	.db #0xff	; 255
   44BA FF                  535 	.db #0xff	; 255
   44BB FB                  536 	.db #0xfb	; 251
   44BC F7                  537 	.db #0xf7	; 247
   44BD FF                  538 	.db #0xff	; 255
   44BE BB                  539 	.db #0xbb	; 187
   44BF 77                  540 	.db #0x77	; 119	'w'
   44C0 FF                  541 	.db #0xff	; 255
   44C1 FF                  542 	.db #0xff	; 255
   44C2 FB                  543 	.db #0xfb	; 251
   44C3 F7                  544 	.db #0xf7	; 247
   44C4 FF                  545 	.db #0xff	; 255
   44C5 BB                  546 	.db #0xbb	; 187
   44C6 77                  547 	.db #0x77	; 119	'w'
   44C7 FF                  548 	.db #0xff	; 255
   44C8 FF                  549 	.db #0xff	; 255
   44C9 FF                  550 	.db #0xff	; 255
   44CA FF                  551 	.db #0xff	; 255
   44CB FF                  552 	.db #0xff	; 255
   44CC FF                  553 	.db #0xff	; 255
   44CD FF                  554 	.db #0xff	; 255
   44CE FF                  555 	.db #0xff	; 255
   44CF FF                  556 	.db #0xff	; 255
   44D0 FF                  557 	.db #0xff	; 255
   44D1 FF                  558 	.db #0xff	; 255
   44D2 FF                  559 	.db #0xff	; 255
   44D3 FF                  560 	.db #0xff	; 255
   44D4 FF                  561 	.db #0xff	; 255
   44D5 FF                  562 	.db #0xff	; 255
   44D6 FF                  563 	.db #0xff	; 255
   44D7 FF                  564 	.db #0xff	; 255
   44D8 FF                  565 	.db #0xff	; 255
   44D9 FF                  566 	.db #0xff	; 255
   44DA FF                  567 	.db #0xff	; 255
   44DB FF                  568 	.db #0xff	; 255
   44DC FF                  569 	.db #0xff	; 255
   44DD FF                  570 	.db #0xff	; 255
   44DE FF                  571 	.db #0xff	; 255
   44DF FF                  572 	.db #0xff	; 255
   44E0 FF                  573 	.db #0xff	; 255
   44E1 FF                  574 	.db #0xff	; 255
   44E2 FF                  575 	.db #0xff	; 255
   44E3 FF                  576 	.db #0xff	; 255
   44E4 FF                  577 	.db #0xff	; 255
   44E5 AB                  578 	.db #0xab	; 171
   44E6 57                  579 	.db #0x57	; 87	'W'
   44E7 FF                  580 	.db #0xff	; 255
   44E8 FF                  581 	.db #0xff	; 255
   44E9 FF                  582 	.db #0xff	; 255
   44EA FF                  583 	.db #0xff	; 255
   44EB FF                  584 	.db #0xff	; 255
   44EC AB                  585 	.db #0xab	; 171
   44ED 57                  586 	.db #0x57	; 87	'W'
   44EE FF                  587 	.db #0xff	; 255
   44EF FF                  588 	.db #0xff	; 255
   44F0 FF                  589 	.db #0xff	; 255
   44F1 FF                  590 	.db #0xff	; 255
   44F2 FF                  591 	.db #0xff	; 255
   44F3 FF                  592 	.db #0xff	; 255
   44F4 FF                  593 	.db #0xff	; 255
   44F5 FF                  594 	.db #0xff	; 255
   44F6 FF                  595 	.db #0xff	; 255
   44F7 FF                  596 	.db #0xff	; 255
   44F8 FF                  597 	.db #0xff	; 255
   44F9 FF                  598 	.db #0xff	; 255
   44FA FF                  599 	.db #0xff	; 255
   44FB FF                  600 	.db #0xff	; 255
   44FC FF                  601 	.db #0xff	; 255
   44FD FF                  602 	.db #0xff	; 255
   44FE FF                  603 	.db #0xff	; 255
   44FF FF                  604 	.db #0xff	; 255
   4500 FF                  605 	.db #0xff	; 255
   4501 FF                  606 	.db #0xff	; 255
   4502 FF                  607 	.db #0xff	; 255
   4503 FF                  608 	.db #0xff	; 255
   4504 FF                  609 	.db #0xff	; 255
   4505 FF                  610 	.db #0xff	; 255
   4506 FF                  611 	.db #0xff	; 255
   4507 FF                  612 	.db #0xff	; 255
   4508 FF                  613 	.db #0xff	; 255
   4509 FF                  614 	.db #0xff	; 255
   450A FF                  615 	.db #0xff	; 255
   450B FF                  616 	.db #0xff	; 255
   450C FF                  617 	.db #0xff	; 255
   450D FF                  618 	.db #0xff	; 255
   450E FF                  619 	.db #0xff	; 255
   450F FB                  620 	.db #0xfb	; 251
   4510 F7                  621 	.db #0xf7	; 247
   4511 FF                  622 	.db #0xff	; 255
   4512 FB                  623 	.db #0xfb	; 251
   4513 F7                  624 	.db #0xf7	; 247
   4514 FF                  625 	.db #0xff	; 255
   4515 FF                  626 	.db #0xff	; 255
   4516 FB                  627 	.db #0xfb	; 251
   4517 F7                  628 	.db #0xf7	; 247
   4518 FF                  629 	.db #0xff	; 255
   4519 FB                  630 	.db #0xfb	; 251
   451A F7                  631 	.db #0xf7	; 247
   451B FF                  632 	.db #0xff	; 255
   451C FF                  633 	.db #0xff	; 255
   451D FF                  634 	.db #0xff	; 255
   451E FF                  635 	.db #0xff	; 255
   451F FF                  636 	.db #0xff	; 255
   4520 FF                  637 	.db #0xff	; 255
   4521 FF                  638 	.db #0xff	; 255
   4522 FF                  639 	.db #0xff	; 255
   4523 FF                  640 	.db #0xff	; 255
   4524 FF                  641 	.db #0xff	; 255
   4525 FF                  642 	.db #0xff	; 255
   4526 FF                  643 	.db #0xff	; 255
   4527 FF                  644 	.db #0xff	; 255
   4528 FF                  645 	.db #0xff	; 255
   4529 FF                  646 	.db #0xff	; 255
   452A FF                  647 	.db #0xff	; 255
   452B FF                  648 	.db #0xff	; 255
   452C FF                  649 	.db #0xff	; 255
   452D FF                  650 	.db #0xff	; 255
   452E FF                  651 	.db #0xff	; 255
   452F FF                  652 	.db #0xff	; 255
   4530 FF                  653 	.db #0xff	; 255
   4531 FF                  654 	.db #0xff	; 255
   4532 FF                  655 	.db #0xff	; 255
   4533 FF                  656 	.db #0xff	; 255
   4534 FF                  657 	.db #0xff	; 255
   4535 FF                  658 	.db #0xff	; 255
   4536 FF                  659 	.db #0xff	; 255
   4537 FF                  660 	.db #0xff	; 255
   4538 FF                  661 	.db #0xff	; 255
   4539 FB                  662 	.db #0xfb	; 251
   453A F7                  663 	.db #0xf7	; 247
   453B FF                  664 	.db #0xff	; 255
   453C AB                  665 	.db #0xab	; 171
   453D 57                  666 	.db #0x57	; 87	'W'
   453E FF                  667 	.db #0xff	; 255
   453F FF                  668 	.db #0xff	; 255
   4540 FB                  669 	.db #0xfb	; 251
   4541 F7                  670 	.db #0xf7	; 247
   4542 FF                  671 	.db #0xff	; 255
   4543 AB                  672 	.db #0xab	; 171
   4544 57                  673 	.db #0x57	; 87	'W'
   4545 FF                  674 	.db #0xff	; 255
   4546 FF                  675 	.db #0xff	; 255
   4547 FF                  676 	.db #0xff	; 255
   4548 FF                  677 	.db #0xff	; 255
   4549 FF                  678 	.db #0xff	; 255
   454A FF                  679 	.db #0xff	; 255
   454B FF                  680 	.db #0xff	; 255
   454C FF                  681 	.db #0xff	; 255
   454D FF                  682 	.db #0xff	; 255
   454E FF                  683 	.db #0xff	; 255
   454F FF                  684 	.db #0xff	; 255
   4550 FF                  685 	.db #0xff	; 255
   4551 FF                  686 	.db #0xff	; 255
   4552 FF                  687 	.db #0xff	; 255
   4553 FF                  688 	.db #0xff	; 255
   4554 FF                  689 	.db #0xff	; 255
   4555 FF                  690 	.db #0xff	; 255
   4556 FF                  691 	.db #0xff	; 255
   4557 FF                  692 	.db #0xff	; 255
   4558 FF                  693 	.db #0xff	; 255
   4559 FF                  694 	.db #0xff	; 255
   455A FF                  695 	.db #0xff	; 255
   455B FF                  696 	.db #0xff	; 255
   455C FF                  697 	.db #0xff	; 255
   455D FF                  698 	.db #0xff	; 255
   455E FF                  699 	.db #0xff	; 255
   455F FF                  700 	.db #0xff	; 255
   4560 FF                  701 	.db #0xff	; 255
   4561 FF                  702 	.db #0xff	; 255
   4562 FF                  703 	.db #0xff	; 255
   4563 BB                  704 	.db #0xbb	; 187
   4564 77                  705 	.db #0x77	; 119	'w'
   4565 FF                  706 	.db #0xff	; 255
   4566 FB                  707 	.db #0xfb	; 251
   4567 F7                  708 	.db #0xf7	; 247
   4568 FF                  709 	.db #0xff	; 255
   4569 FF                  710 	.db #0xff	; 255
   456A BB                  711 	.db #0xbb	; 187
   456B 77                  712 	.db #0x77	; 119	'w'
   456C FF                  713 	.db #0xff	; 255
   456D FB                  714 	.db #0xfb	; 251
   456E F7                  715 	.db #0xf7	; 247
   456F FF                  716 	.db #0xff	; 255
   4570 FF                  717 	.db #0xff	; 255
   4571 FF                  718 	.db #0xff	; 255
   4572 FF                  719 	.db #0xff	; 255
   4573 FF                  720 	.db #0xff	; 255
   4574 FF                  721 	.db #0xff	; 255
   4575 FF                  722 	.db #0xff	; 255
   4576 FF                  723 	.db #0xff	; 255
   4577 FF                  724 	.db #0xff	; 255
   4578 FF                  725 	.db #0xff	; 255
   4579 FF                  726 	.db #0xff	; 255
   457A FF                  727 	.db #0xff	; 255
   457B FF                  728 	.db #0xff	; 255
   457C FF                  729 	.db #0xff	; 255
   457D FF                  730 	.db #0xff	; 255
   457E FF                  731 	.db #0xff	; 255
   457F FF                  732 	.db #0xff	; 255
   4580 FF                  733 	.db #0xff	; 255
   4581 FF                  734 	.db #0xff	; 255
   4582 FF                  735 	.db #0xff	; 255
   4583 FF                  736 	.db #0xff	; 255
   4584 FF                  737 	.db #0xff	; 255
   4585 FF                  738 	.db #0xff	; 255
   4586 FF                  739 	.db #0xff	; 255
   4587 FF                  740 	.db #0xff	; 255
   4588 F3                  741 	.db #0xf3	; 243
   4589 FF                  742 	.db #0xff	; 255
   458A FF                  743 	.db #0xff	; 255
   458B FF                  744 	.db #0xff	; 255
   458C FF                  745 	.db #0xff	; 255
   458D FF                  746 	.db #0xff	; 255
   458E FF                  747 	.db #0xff	; 255
   458F F3                  748 	.db #0xf3	; 243
   4590 FF                  749 	.db #0xff	; 255
   4591 FF                  750 	.db #0xff	; 255
   4592 FF                  751 	.db #0xff	; 255
   4593 FF                  752 	.db #0xff	; 255
   4594 FF                  753 	.db #0xff	; 255
   4595 FF                  754 	.db #0xff	; 255
   4596 F3                  755 	.db #0xf3	; 243
   4597 FF                  756 	.db #0xff	; 255
   4598 FF                  757 	.db #0xff	; 255
   4599 FF                  758 	.db #0xff	; 255
   459A FF                  759 	.db #0xff	; 255
   459B FF                  760 	.db #0xff	; 255
   459C FF                  761 	.db #0xff	; 255
   459D FF                  762 	.db #0xff	; 255
   459E FF                  763 	.db #0xff	; 255
   459F FF                  764 	.db #0xff	; 255
   45A0 FF                  765 	.db #0xff	; 255
                            766 	.area _INITIALIZER
                            767 	.area _CABS (ABS)
