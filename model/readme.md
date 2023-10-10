# Unsupervised Approach <sup>[1]</sup>

## Reconstruction-based methods
The core idea is to conduct encoding and decoding on the input normal images and train the neural network with the aim of reconstruction. Based on the assumption
that by training only on normal images, the model will not be able to reconstruct abnormal images correctly, and the anomaly scores will be higher.

Classical methods based on reconstruction include autoencoders (AE [122], [123]) , variational auto-encoders (VAE [124]) and generative adversarial networks (GAN [125]).

* Ven.,CAVGA [92];
* Liu,UTAD [93];
* Yang,DFR [94];
* Mo.,STPM [95];
* Yamada,RSTPM [96];
* Deng,RDOE [97];
* Rudolph,AST [98];
* Massoli,MOCCA [99];
* Liang,OCR-GAN [100];
* Mishra,VT-ADL [101];
* Li,SOMAD [102]

## Normalizing Flow(NF)-based methods
NF is able to learn transformations between data distributions and well-defined probability density functions, which can serve as a suitable estimator of probability densities for the purpose of detecting anomalies.
* Rudolph,Differnet [103];
* Gudovskiy,CFlow [104];
* Rudolph,FCCSF [105];
* Yu,FastFlow [106]


## Representation-based methods
Deep neural networks are used to extract meaningful vectors describing the image, and the anomaly score is usually represented by distance calculation.
* Cohen,SPADE [107];
* Defard,PaDIM [108];
* Kars.,PatchCore [109];
* Wang,GP [110];
* Zheng,FYD [111];
* Rip.,Gaussian-AD [112];
* Yi,Patch SVDD [113];
* DisAug CLR [114];
* Ki.,Semi-orth [115];
* Lee,CFA [116]


## Data augmentation-based methods
Augmentation algorithms are designed to resemble anomalies
* Zav.,DRAEM [117];
* Schluter,NSA [118];
* Li,CutPaste [119];
* Nicolae,SSPCAB [120];
* Song,AnoSeg [121]


## References
[1] Y. Cui et al.: A Survey on Unsupervised Anomaly Detection Algorithms for Industrial Images