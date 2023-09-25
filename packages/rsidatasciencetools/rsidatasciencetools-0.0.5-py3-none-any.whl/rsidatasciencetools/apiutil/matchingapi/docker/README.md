## Matching API Docker Image

The docker container is the preferred method of deployment for RSI's ML models. In this module, the API is defined in `rsidatasciencetools/apituil/matchingapi`, and the instructions for testing locally with `uvicorn` are in the base [README](../README.md).

Docker compose is the underlying tool being used to construct both the base ML API image, and the forms-specific NLP-based PII / calculated field classifier.

To build and run the docker container, start from the base directory of this package and run

```
    cd rsidatasciencetools/apiutil/matchingapi/docker

    ./build.sh

    ./run_docker.sh
```

You can verify the container is running by running `docker ps` and looking for a container with the name `rsi.revx.forms/forms.matching_api` with a `Up X hours` status.

To test is the API is being hosted correctly, you can navigate to both of the following URLs to see whether the process is up (supervisord control panel), and if the Swagger documentation API is available, respectivley

```
    http://localhost:9001
    http://localhost:8000/v1.0/docs
```