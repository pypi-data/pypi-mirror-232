# Non-Matching Audio Distance (NOMAD)

### Purpose
NOMAD is a differentiable perceptual similarity metric that measures the distance of a degraded signal against non-matching references (unpaired speech).
The proposed method is based on learning deep feature embeddings via a triplet loss guided by the Neurogram Similarity Index Measure (NSIM) to capture degradation intensity. During inference, the similarity score between any two audio samples is computed through Euclidean distance of their embedding.
NOMAD can be also used as a loss function to improve speech enhancement models.

### More Information
For additional information on NOMAD see the [preprint](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10096274). 

## Installation
NOMAD is hosted on PyPi. It can be installed in your Python environment with the following command
```
pip install nomad_audio
```

## Using NOMAD
QAMA has been evaluated with a 3-fold cross-validation. We provide the 3 models plus a model trained using the full Vinylset.
* ```qama_fold1.pt```
* ```qama_fold2.pt```
* ```qama_fold3.pt```
* ```qama_full.pt```

To predict the quality of your music collection, organise files in a directory and run:

```python predict.py --data_dir /path/to/dir/collection```

The script creates a csv file in ```prediction_files``` with date time format ```DD-MM-YYYY_hh-mm-ss_qama.csv```
The csv files includes predictions of the 4 models and the average of the 3 cross-validation models. This is defined with the column ```Mean CV```.
### Full Model
The model ```qama_full.pt``` is trained using all the Vinylset tracks. Unlike the cross-validation models, the full model has not been evaluated in the ICASSP paper although it might be more accurate. 
Informal tests show aligned results with the cross-validation models.

You can set ```full_model=False``` if you do not want to use QAMA full.

### Correct usage
QAMA has been evaluated for vinyl degradations and using files around 10 seconds. The model accepts variable input length but it was not evaluated for very long tracks. 

## Paper and license
If you use QAMA or Vinylset please cite this [paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10096274): 

A. Ragano, E. Benetos, and A. Hines "Audio Quality Assessment of Vinyl Music Collections using Self-Supervised Learning", in IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP) 2023.


The code is licensed under MIT license.

