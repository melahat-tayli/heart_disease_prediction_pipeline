# Final Project
[![Build Status](https://travis-ci.com/melahat-tayli/2020fa-final-project-melahat-tayli.svg?token=dgPsxw4xayEVSd1T3haz&branch=master)](https://travis-ci.com/melahat-tayli/2020fa-final-project-melahat-tayli)

### Description:
This project builds an automated data analysis pipeline using the Luigi python package. Additionally, the Bokeh python library has been used for interactive visualization of raw data histograms.
Bokeh was integrated into the Django app [1].
The project has two packages: `final-project` and `Visualizer`:
* `final-project` package implements the `luigi` tasks,
* `Visualizer` package implements the interactive visualization of raw data.


### Installation:
This project uses Pipenv to build and manage the above described application and uses python 3.7.
```
conda create -n py37 python=3.7
conda activate py37
pip install pipenv
```

To install dependencies as well as development packages such as pytest, first set the working directory to this repository and use the following command:
```
pipenv install --dev
```

To run the luigi pipeline:
```
pipenv run python -m final_project
```

To see the interactive visualization of the raw data:
change directory to Visualizer, where the `manage.py` file is.
Then use the following command to run the server:
```
pipenv run python manage.py runserver
```
This will give a link (`http://127.0.0.1:8000/`)
Open up `http://127.0.0.1:8000/visualization/` to see the interactive bar plots.

To reach amazon s3 bucket:
Make a .env file in the root directory (where `README.md` file is) and write your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to `.env` file.


### Details of final-project package:
There are four modules for luigi tasks and one module for data-specific preprocessing (`preprocess_heart.py`).
In this repo, data folder (in the root directory) keeps the data that will be analyzed.
Also; models, graphs etc. are created in the data folder after running the luigi pipeline.

Luigi tasks are shared between the four modules: `load_data.py`, `preprocess_data.py`, `train.py`, `testperformance_model.py`


#### `load_data` module:
This module implements UploadRawData, DownloadRawData, RawData and TrainTestSplit Tasks.

* `UploadRawData` task uploads the raw data to amazon s3 bucket. This is needed as data is assumed to be in amazon s3 bucket in
the luigi pipeline. This also provides flexibility to work on different computers. Once data is uploaded to amazon s3
bucket, it is easy to reach it using the luigi pipeline. `UploadRawData` is not a part of the luigi pipeline.

* `DownloadRawData` task downloads the data to `data` folder. `Visualization` app reaches data from local data folder.

* `RawData` task is an external luigi task. It's output returns the `S3Target` which contains the raw data.

* `TrainTestSplit` task splits raw data as _train_ and _test_, then returns train or test data depending on the `train_or_test` parameter.
If `train_or_test='train'`, it returns train data; if `train_or_test='test'`, it returns test data as csv file.


#### `preprocess_data` module:
This module imports the function `preprocess` from `preprocessing_heart.py`. If an alternative data set
is to be used, a new `preprocess` function should be written and imported.
`preprocess_data` module implements a `PreProcessing` task. This task receives two parameters: `data` and `train_or_test` parameter.
* `data parameter` is the name of the data to be analyzed. In this project `heart.csv` [2] data is used.
* `train_or_test` parameter addresses to which part of the data is used (`'train'` or `'test'`)


#### `train module:`
This module implements a task named `Train`.
`Train` task takes data name, sklearn model name and train part of the data as parameters. It saves the trained model to data folder.
Also, when running this Task, model name and train score will be printed on the screen. Model names and train scores will be
also saved to `trainscores.csv` file in the data folder.


#### `testperformance_model` module:
This module  implements `TestModel` task.
`TestModel` task takes data name, train part of the data (`source_train`), test part of the data (`source_test`) and `model` name as parameters.
This task loads the trained model and applies it on the test data. Model performance on the test data printed on the screen while running this task.
Also, an automatic plotting file (plotting.png) is formed in tha data folder. This plot shows the bar plot of the model scores.

#### References:
[1] Visualizer package is implemented by taking advantage of bokeh github repository.
https://github.com/bokeh/bokeh/tree/branch-2.3/examples/app/crossfilter
https://github.com/bokeh/bokeh/tree/branch-2.3/examples/howto/server_embed/django_embed

[2] heart data is taken from kaggle data set.
https://www.kaggle.com/ronitf/heart-disease-uci
