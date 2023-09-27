# Quantifying the Displacement of Data-Matrix-Code Modules: A Comparative Study of Different Approximation Approaches for Predictive Maintenance of Drop-on-Demand Printing Systems


by
[Peter Bischoff](peter.bischoff@ikts.fraunhofer.de),
André V. Carreiro,
Christiane Schuster,
Thomas Härtling


This Paper has been submitted for publication in the "Journal of Imaging" on 
May 30th 2023. 

## Abstract
Drop-on-Demand printing using colloidal or pigmented inks is prone to
clogging of printing nozzles which can lead to positional deviations and
inconsistently printed patterns (e g. data matrix codes, DMCs). However, if such
deviations are detected early, they can be useful for determining the state of
the print head and plan maintenance operations prior to reaching a printing
state where the printed DMCs are unreadable. To realize this predictive
maintenance approach, it is necessary to accurately quantify the positional
deviation of individually printed dots from the actual target position. Here we
present a comparison of different methods based on affinity transformations and
clustering algorithms to calculate the printed position, the target position,
and the deviation of both for complete DMCs. Hence, our method focuses on the
evaluation of the print quality, not on decoding of DMCs. We compare our results
to state-of-the-art recognition and decoding algorithms and find that we can
determine the occurring deviations with significantly higher accuracy especially
when the printed DMCs are of low quality. The results enable the development of
decision systems for predictive maintenance and subsequently the optimization of
printing systems.



## Installation
You'll need a working Python environment to run the code.
To create a Python environment, which does not interfere with your systems installation of Python, we recommend using [Anaconda](https://www.anaconda.com/download/). 

To create a new environment and install the package, from the root of this repository run:
```py
conda create gridfinder python=3.9
pip install . --upgrade
```

## Recreating the Results
To recreate the results run `python runtime.py` and `python simulation.py`. 
This will create the results described in section 3.1 and 3.2.  
To create the results from section 3.3 additional data and source code is needed, which cannot be published. Please contact the authors for details.

## Usage
Example:
```py
from gridfinder.unguided import UGAT
targets = UGAT.approximate_grid(blob_positions) 
``` 

## License

All source code is made available under a MIT license. See `LICENSE.md` for the full license text.
