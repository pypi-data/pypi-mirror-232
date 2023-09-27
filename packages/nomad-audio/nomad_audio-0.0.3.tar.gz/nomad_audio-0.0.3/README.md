# Non-Matching Audio Distance (NOMAD)

NOMAD is a differentiable perceptual similarity metric that measures the distance of a degraded signal against non-matching references (unpaired speech).
The proposed method is based on learning deep feature embeddings via a triplet loss guided by the Neurogram Similarity Index Measure (NSIM) to capture degradation intensity. During inference, the similarity score between any two audio samples is computed through Euclidean distance of their embedding.
NOMAD can be also used as a loss function to improve speech enhancement models.

## Installation
NOMAD is hosted on PyPi. It can be installed in your Python environment with the following command
```
pip install nomad_audio
```

## Using NOMAD Similarity Score
### Using NOMAD from the command line
NOMAD similarity score can be used to measure perceptual similarity between any two signals. NOMAD can be used with unpaired speech i.e., any clean speech can serve as a reference. You can use NOMAD from the command line as follows:  

```
python -m nomad_audio --nmr_path /path/to/dir/references --test_path /path/to/dir/degraded
```

The script creates two csv files in ```results-csv``` with date time format. 
* ```DD-MM-YYYY_hh-mm-ss_nomad_avg.csv``` includes the average NOMAD scores with respect to all the references in ```nmr_path``` 
* ```DD-MM-YYYY_hh-mm-ss_nomad_scores.csv``` includes pairwise scores between the degraded speech samples in ```test_path``` and the references in ```nmr_path```

You can choose where to save the csv files by setting ```results_path```. 

### Using NOMAD inside Python
You can import NOMAD as a module in Python. Here is an example:

```{python}
from nomad_audio import nomad 

nmr_path = 'data/nmr-data'
test_path = 'data/test-data'

nomad_avg_scores, nomad_scores = nomad.predict(nmr_path, test_path)
```

## Using NOMAD loss function
NOMAD has been evaluated as a loss function to improve speech enhancement models. The NOMAD loss is the sum of the L1 distance between the clean and the estimated speech extracted at each transformer layer and at the embedding layer.

NOMAD loss can be used as a PyTorch loss function as follows:
```{python}
from nomad_audio import nomad 

# Here is your training loop where you calculate your loss
loss = mse_loss(estimate, clean) + weight * nomad.forward(estimate, clean)
```

We provide a full example on how to use NOMAD loss for speech enhancement using a wave U-Net architecture, see ```src/nomad_audio/nomad_loss_test.py```.
In this example we show that using NOMAD as an auxiliary loss you can get quality improvement:
* Baseline using only MSE, PESQ = 2.39
* Using MSE + NOMAD loss, PESQ = 2.60

See paper for more details on speech enhancement results using the model DEMUCS.

### NOMAD loss weight
We recommend to tune the weight of the NOMAD loss. Paper results with the DEMUCS model has been done by setting the weight to `0.1`. 
The U-Net model provided in this repo uses a weight equal to `0.001`.

## Paper and license
Pre-print will be available soon.
The NOMAD code is licensed under MIT license.