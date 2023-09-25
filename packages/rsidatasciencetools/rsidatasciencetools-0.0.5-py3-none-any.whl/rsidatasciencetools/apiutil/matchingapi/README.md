### ML Embedding API for Record-Matching

This module will run an API which can take in JSON or string data via a request potential matching in the database specified for the tenant database info (submitting via the `set_matching_config` request).

More details on operation will be added later, for now, ensure python and related dependencies are installed; to run the API, navigate to the `rsidatasciencetools/aptutil/matchigapi` folder and run 

``` python app.py [-r]```

The command line options can be displayed by providing the `-h` help flag. You can pull up the swagger-based interactive documentation by navigating to the [localhost rendered page](http://localhost:8000/v1.0/docs) (i.e., http://localhost:8000/v1.0/docs).

