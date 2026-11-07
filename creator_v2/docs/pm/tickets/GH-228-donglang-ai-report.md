# GH-228 ? B?o c?o g?n ?nh v? clip AI

**Ch?a ho?n t?t:** c?ng long_gate ch?a ??T v? thi?u TTS; ticket c?m ch?y TTS. Ph?p ??c l??ng ??c l?p c?n ph?t hi?n c?nh ng?n, c?n Lead x? l? tr??c b??c d?ng.

?? thay c?c clip 1981xx, g?n 16 ?nh AI, `credit: false`, ch? th?ch t?i d?ng; ?? khai ?nh trong spec v? c?p nh?t gen_scenes.py. Gi? nguy?n `lines`; kh?ng ch?y TTS ho?c render. Kh?ng ch?y b? sinh v? b?n hi?n t?i ??c spec c?a ?? t?i kh?c, ngo?i ph?m vi cho ph?p; do ?? ch?a ki?m ch?ng t?i sinh ??u ra.

## T?i nguy?n ? c?nh (??nh s? c?nh t? 1)

| T?i nguy?n | Ch??ng#c?nh |
|---|---|
| 900001 | ch00#7, ch03#13, ch06#11, ch13#17 |
| 900002 | ch00#22, ch01#18, ch09#21, ch10#14 |
| 900003 | ch01#21, ch02#9, ch02#13, ch03#5 |
| 900004 | ch05#15, ch06#23 |
| 900005 | ch04#13, ch08#8, ch08#18 |
| 900006 | ch11#17 |
| ai01 | ch00#2 |
| ai02 | ch00#6 |
| ai03 | ch00#11 |
| ai04 | ch01#24 |
| ai05 | ch02#7 |
| ai06 | ch02#10 |
| ai07 | ch03#30 |
| ai08 | ch04#20 |
| ai09 | ch05#3 |
| ai10 | ch06#14 |
| ai11 | ch07#13 |
| ai12 | ch08#13 |
| ai13 | ch09#27 |
| ai14 | ch10#26 |
| ai15 | ch11#16 |
| ai16 | ch13#22 |

C?nh c?n 1981xx: kh?ng c?.

## S? c?nh m?i lo?i

- bars: 1
- broll: 34
- counter: 3
- date: 32
- file: 34
- kinetic: 118
- ledger: 23
- map: 8
- org: 4
- photo: 59
- question: 5
- quote: 1
- slam: 61
- split: 3
- timeline: 4

## Ki?m tra

- `python scripts/long_gate.py dong-lang --min-syl 1900`: TR??T, ch? l?i ch?a TTS 14 ch??ng; 5.665 ?m ti?t, 390 c?nh.
- `python scripts/long_gate.py dong-lang --min-syl 5000`: TR??T, c?ng l?i ch?a TTS.
- `floor.problems(chapters, channel="CL", topic="dong-lang")`: `[]`.
- `PYTHONIOENCODING=utf-8 python motion/variety.py audit dong-lang`: OK.
- `python motion/long/scene_params.py dong-lang`: kh?ng l?i, kh?ng c?nh b?o.
- L?nh ki?m m?t d?u trong brief: `[]`.
- T? ??c t?nh theo 4,2 ?m ti?t/gi?y, c?ng kho?ng ngh?: 36 c?nh d??i 2,5 gi?y: ch00#7 (2.14s), ch00#18 (2.38s), ch00#19 (2.14s), ch01#4 (2.38s), ch01#11 (2.38s), ch01#18 (2.14s), ch01#20 (2.14s), ch01#23 (2.38s), ch02#9 (2.38s), ch02#10 (2.38s), ch02#13 (2.38s), ch02#17 (2.43s), ch02#18 (2.38s), ch02#29 (2.38s), ch03#7 (2.38s), ch03#10 (2.14s), ch03#11 (2.14s), ch03#20 (2.14s), ch03#21 (2.14s), ch03#25 (2.38s), ch04#5 (2.38s), ch04#21 (2.38s), ch06#2 (2.38s), ch06#4 (2.14s), ch06#23 (2.38s), ch06#24 (2.38s), ch07#9 (2.14s), ch07#15 (2.38s), ch07#17 (2.14s), ch08#22 (2.43s), ch09#15 (2.38s), ch09#18 (2.38s), ch12#7 (2.38s), ch12#28 (2.38s), ch13#2 (2.14s), ch13#3 (2.14s). Ph??ng ph?p ??c t?nh ch?a thay th? timing TTS; ch?a ch?nh m?c.
- `ffprobe` s?u clip: Permission denied khi m? t?p; c? th? th?y t?p t?n t?i nh?ng ch?a x?c minh th?i l??ng th?c ho?c gi?i h?n c?nh ng?n h?n clip 0,5 gi?y.
- Ch?a x?c minh ??y ?? m?c ph?n t? con th? hai ? 1 gi?y; ch?a soi clip sheet ho?c thumbnail v? ticket c?m render v? kh?ng t?o m?i c?c t? so?t.
- Kh?ng ki?m l?i c?c kh?ng ??nh trong l?i ??c; ticket y?u c?u gi? nguy?n l?i ??c.

Clip sheet / thumbnail: kh?ng t?o trong ticket n?y; ch?a ki?m tra tr?c quan.
