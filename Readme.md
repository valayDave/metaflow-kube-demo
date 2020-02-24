# Metaflow Kubernetes Plugin Testing

- Constraints : 
    - Currently tested with Minikube
    - Supports S3 based Datastore. Wont work without S3 as datastore. 

## Setting Up Environment
- Install Minikube
- Replace in AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_SESSION_TOKEN in `setup.sh`
- ``sh setup.sh``

## Checking Jobs on Kube : 
- ``kubectl get jobs``
- ``kubectl describe jobs/<jobid>``

## Seeing Results Post Completion 
- check [experiments_analytics.ipynb](experiments_analytics.ipynb)