## Steps To Push An Image Into Amazon ECR With Docker
#### step 1: Log in to AWS elastic container registry
 Use the get-login command to log in to AWS elastic container registry and save it to a text file 
```bash
aws ecr get-login --region ap-south-1 > text.txt
```
#### step 2: Authenticate Docker to AWS elastic container registry
```bash
docker login -u AWS https://aws_account_id.dkr.ecr.ap-south-1.amazonaws.com #Replace the aws account id
Password: ***** #past password here
```
#### step 3: Create a repository
```bash
aws ecr create-repository --repository-name mlflow-server
```
#### step 4: Build the Docker image
```bash
docker build -t aws_account_id.dkr.ecr.ap-south-1.amazonaws.com/mlflow-server . #Replace the aws account id
```
#### step 5: push the Docker image
```bash
docker push aws_account_id.dkr.ecr.ap-south-1.amazonaws.com/mlflow-server #Replace the aws account id
```



