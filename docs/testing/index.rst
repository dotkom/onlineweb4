Testing
=======

.. toctree::
   :maxdepth: 2

Onlineweb4 ships with a makefile for simple test running.


Local Testing
-------------

The Makefile contains some shortcut commands for testing the application;

* :code:`make lint-backend`
* :code:`make lint-frontend`
* :code:`make lint-only` (the above two)
* :code:`make test-backend`
* :code:`make test-frontent`
* :code:`make test-only` (the above two)
* :code:`make test` (all of the above)

All of these commands are executed using Docker, which mirrors how we do CI.


Continuous Integration
----------------------

Unit and integration tests are run on every git push to GitHub using Docker through the CI system `Drone CI <https://drone.io>`_. Each test run is ran in a separate docker container, which makes sure each test run has a similar starting point (no leftover files from the previous run etc.).


Custom Docker image for testing
+++++++++++++++++++++++++++++++

The Drone config file uses a custom home made Docker image for OW4 with some predefined dependencies (Dockerfile.testbase), like Python and Node.JS in the same image (usually they are in different Docker images).

If needed, this image can be updated (Dockerfile.testbase), built and pushed to our private Docker registry. To do this, follow these steps:

* Make changes to the Dockerfile
* Build the dockerfile, and name it "registry.online.ntnu.no/dotkom/onlineweb4-testbase". This is done as such: 

  :code:`docker build -f Dockerfile.testbase -t registry.online.ntnu.no/dotkom/onlineweb4-testbase .`

:code:`-f` specifies which dockerfile to use and :code:`-t` specifies the target name of the produced image (as a docker image :code:`name:tag`).

* Propose the Dockerfile changes as a Pull Request
* When the changes are approved and merged, push the docker image to the private repository
* :code:`docker login registry.online.ntnu.no`
* :code:`docker push registry.online.ntnu.no/dotkom/onlineweb4-testbase`

Voilà! New version of the image pushed.
