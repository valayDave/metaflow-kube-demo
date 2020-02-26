echo "Starting Minikube"
minikube start --cpus 6 --memory 6000   
echo "Installing Repo"
python3 -m venv .env
.env/bin/pip install https://github.com/valayDave/metaflow/archive/kube_cpu_stable.zip
.env/bin/pip install -r requirements.txt
echo "Downloading Data"
.env/bin/python download_mnist.py
echo "Exporting Keys"
export AWS_ACCESS_KEY_ID=<ACCESS_KEY_COMES_HERE>
export AWS_SECRET_ACCESS_KEY=<ACCESS_SECRET_KEY_COMES_HERE>
export AWS_SESSION_TOKEN=<ACCESS_SESSION_TOKEN_COMES_HERE>
export AWS_DEFAULT_REGION='us-east-1'
export METAFLOW_DATASTORE_SYSROOT_LOCAL=$(pwd)
export METAFLOW_DATASTORE_SYSROOT_S3=s3://<PATH_TO_BUCKET>
echo "Running it on Minikube"
.env/bin/python multi_step_mnist.py --with kube:cpu=3,memory=4000,image=tensorflow/tensorflow:latest-py3 run --num_training_examples 10000
