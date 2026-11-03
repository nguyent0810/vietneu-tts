# Creative wall time per topic (epoch s, measured; includes reading facts of that topic is NOT separated: all fact stores were read first at 1793715304..)
overall_start 1793715304
bud_vessantara start 1793715359 end 1793715359
bud_angulimala start 1793715381 end 1793715381
fs_mau_than_1968_2027 start 1793715409 end 1793715409
fs_quet_nha_mung1_tet start 1793715434 end 1793715434
vsd_thanh_nha_ho start 1793715459 end 1793715459
vsd_bach_dang_1288 start 1793715489 end 1793715489

Note: start/end stamps bracket only the file-write command (sub-second). Wall time per topic including composing = gap between consecutive end stamps:
- reading all 6 fact stores + history + prompt: 1793715304 -> 1793715341 (~37 s, shared)
- bud_vessantara: ~18 s after 1793715341 (end 1793715359)
- bud_angulimala: 22 s (1793715359 -> 1793715381)
- fs_mau_than_1968_2027: 28 s (-> 1793715409)
- fs_quet_nha_mung1_tet: 25 s (-> 1793715434)
- vsd_thanh_nha_ho: 25 s (-> 1793715459) plus a small patch edit after
- vsd_bach_dang_1288: 30 s (-> 1793715489)
Total ~3 min 05 s end to end (overall_start 1793715304 -> 1793715489).
