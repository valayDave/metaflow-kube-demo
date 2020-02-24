# Metaflow Kubernetes Plugin Testing

- Constraints : 
    - Currently tested with Minikube
    - Supports S3 based Datastore. Wont work without S3 as datastore. 
    - Supports Conda Decorators. Current ``setup.sh`` uses tensorflow/tensorflow image. 
    - To use conda Add the following : 
        - ``@conda_base(python=get_python_version(),libraries={'numpy':'1.18.1','tensorflow':'1.4.0','python-kubernetes':'10.0.1'})`` above the class definition to make it work with conda.
        - TO run with conda change the line in setup.sh to following : 
            - ``.env/bin/python hello_mnist.py --environment=conda --with kube:cpu=2,memory=4000,image=python:3.7 run --num_training_examples 2500``
    

## Setting Up Environment
- Install Minikube
- Replace in AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_SESSION_TOKEN in `setup.sh`
- ``sh setup.sh``

## Checking Jobs on Kube : 
- ``kubectl get jobs``
- ``kubectl describe jobs/<jobid>``

## Seeing Results Post Completion 
- check [experiments_analytics.ipynb](experiments_analytics.ipynb)