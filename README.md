# automate_script

## installation instructions

```
git clone git@github.com:Shirsendu-Sarkar/automate_script1.git
```
```
cd automate_script1
```
```
git checkout develop
```
```
check in console 'python3 --version' if not installed type 'sudo apt install python3'
```
```
pip3 install virtualenv
```
```
virtualenv venv
```
```
source venv/bin/activate
```
```
pip3 install -r requirements.txt
```
```
sudo npm install serverless-plugin-git-variables serverless-python-requirements @ljxau/serverless-dynamodb-autoscaling serverless-plugin-aws-resolvers serverless-log-forwarding serverless-pseudo-parameters
```
```
sls invoke local -f index
```
