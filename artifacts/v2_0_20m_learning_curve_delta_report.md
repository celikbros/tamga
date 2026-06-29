# v2.0 20M Learning Curve Delta Report

This report reads the logged validation checkpoints from the 20M runs and
compares candidates at nearest matched raw-byte checkpoints.

## Delta Versus SP64 Floor

| Target bytes | SP64 bytes | SP64 valid BPB | Self bytes | Self valid BPB | Self delta | Teacher bytes | Teacher valid BPB | Teacher delta |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2,000,000 | 1,608,923 | 3.700883 | 1,604,936 | 3.692259 | -0.008624 | 1,483,168 | 3.677377 | -0.023506 |
| 4,000,000 | 3,217,847 | 2.716352 | 3,209,872 | 2.709774 | -0.006578 | 4,449,505 | 2.420500 | -0.295852 |
| 6,000,000 | 6,435,694 | 2.204375 | 6,419,744 | 2.206778 | +0.002403 | 5,932,673 | 2.266931 | +0.062556 |
| 8,000,000 | 8,044,617 | 2.088419 | 8,024,680 | 2.091747 | +0.003328 | 7,415,841 | 2.151040 | +0.062621 |
| 10,000,000 | 9,653,541 | 2.047196 | 9,629,616 | 2.047923 | +0.000727 | 10,382,177 | 2.072028 | +0.024832 |
| 12,000,000 | 11,262,464 | 2.020156 | 11,234,552 | 2.021108 | +0.000952 | 11,865,346 | 2.050466 | +0.030310 |
| 14,000,000 | 14,480,311 | 1.988485 | 14,444,424 | 1.991335 | +0.002850 | 13,348,514 | 2.033022 | +0.044537 |
| 16,000,000 | 16,089,235 | 1.984723 | 16,049,360 | 1.977787 | -0.006937 | 16,314,850 | 2.000905 | +0.016182 |
| 18,000,000 | 17,698,158 | 1.966560 | 17,654,296 | 1.966493 | -0.000066 | 17,798,018 | 1.990317 | +0.023757 |
| 20,000,000 | 20,002,137 | 1.951192 | 20,000,713 | 1.951182 | -0.000010 | 20,002,006 | 1.971752 | +0.020560 |

## Reading

Teacher-distilled ends worse than SP64. Any early advantage is not durable within this 20M window.

The 2M endpoint from the earlier ladder should not be spliced into
this curve because that run used older accounting. The within-run
20M curve is the cleaner decision artifact.
