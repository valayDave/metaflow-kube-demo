# Metaflow Kubernetes Plugin Testing

- Constraints : 
    - Tested With Kops Cluster(3 master 2 Nodes) and Minikube. No Configuration yet on where to deploy and resource limits. 
    - Supports S3 based Datastore. Wont work without S3 as datastore. 
    - Doesn't support GPU's.  
    - Needs `METAFLOW_KUBE_CONFIG_PATH` and `METAFLOW_KUBE_NAMESPACE` env vars for kubernetes config file and Namespace . Takes `~/.kube/config` and `default` as defaults
    - Requires AWS Secrets in ENV Vars for Deploying PODS
    - Uses Local Metadata Store. 
    - Supports Conda Decorators. Current ``setup.sh`` uses tensorflow/tensorflow image. 
    - To use conda Add the following : 
        - ``@conda_base(python=get_python_version(),libraries={'numpy':'1.18.1','tensorflow':'1.4.0','python-kubernetes':'10.0.1'})`` above the class definition to make it work with conda.
        - TO run with conda change the line in setup.sh to following : 
            - ``.env/bin/python hello_mnist.py --environment=conda --with kube:cpu=2,memory=4000,image=python:3.7 run --num_training_examples 2500``
            - Please also ensure that Conda is in the PATH env variable. 
    
## Setting Up Environment
- Install Minikube
- Replace in AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_SESSION_TOKEN in `setup.sh`
- ``sh setup.sh``

## Using The Plugin 
- Usage is very similar to `@batch` decorator. 
- on top of any `@step` add the `@kube` decorator or use `--with kube:cpu=2,memory=4000,image=python:3.7` in the CLI args. 
- To run with Conda it will need `'python-kubernetes':'10.0.1'` in the libraries argument to `@conda_base` step decorator

## Checking Jobs on Kube : 
- ``kubectl get jobs``
- ``kubectl describe jobs/<jobid>``

## Seeing Results Post Completion 
- check [experiments_analytics.ipynb](experiments_analytics.ipynb)
- Before running notebook use %set_env in notebook to set env vars for AWS Keys. 
