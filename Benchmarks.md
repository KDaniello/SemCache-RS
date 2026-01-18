## V 1.0 (without Bincode и SIMD)
🔥 Benchmark v1.0 Baseline | Items: 100000 | Dim: 128
```text
📥 Put time: 1.7757s
⏱️ Dump time: 4.6937s | Size: 256.80 MB
⏱️ Load time: 10.7910s
⏱️ Avg Search time: 0.3221s
```

## V 1.1 (with Bincode, without SIMD)
🔥 Benchmark v1.0 Baseline | Items: 100000 | Dim: 128
```text
📥 Put time: 1.7522s
⏱️ Dump time: 0.7923s | Size: 108.88 MB
⏱️ Load time: 1.1011s
⏱️ Avg Search time: 0.3050s
```

```text
Dump: 4.7s -> 0.8s (в 6 раз быстрее)
Load: 10.8s -> 1.1s (в 10 раз быстрее)
Size: 257 MB -> 109 MB (в 2.5 раза меньше)
```

## V 1.2 (with Bincode and SIMD)
🔥 Benchmark v1.0 Baseline | Items: 100000 | Dim: 128
```text
📥 Put time: 1.7358s
⏱️ Dump time: 0.7697s | Size: 108.88 MB
⏱️ Load time: 1.1275s
⏱️ Avg Search time: 0.0228s
```

```text
Search time: 0.3s -> 0.022s (22 мс)
Ускорение в 13 раз
```

| Metric | Python/JSON | BaselineRust + Bincode + SIMD | Improvement |
|:-------|:------------|:------------------------------|:------------|
| Dump 100k |	4.7s |	0.77s |	6x faster |
| Load 100k |	10.8s |	1.12s |	10x faster |
| Search | 100k |	322ms |	22ms |	15x faster |
| File Size |	256MB |	109MB |	-57% size |