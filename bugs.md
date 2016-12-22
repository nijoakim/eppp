# BUG
$ epppu network 88120 -c3 -e0 -pe
(220.0 k || (47.00 k + 100.0 k)) = 88.12 k
relative error =
	-123.7 u%

$ epppu network 88123 -c4 -e0 -pe
(2.200 k + (1.000 M || (47.00 k + 47.00 k))) = 88.12 k
relative error =
	246.9 u%

# BUG
$ epppu network 88120 -c5 -e 0.00000
(no printout)
