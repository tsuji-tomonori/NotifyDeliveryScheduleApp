# param
DEPLOY_DIR="deploy/"
SRC_DIR="lambda"

# init
rm ${DEPLOY_DIR} -f -r
mkdir ${DEPLOY_DIR}
cp -r ${SRC_DIR}/* ${DEPLOY_DIR}/

# pip install
cd ${DEPLOY_DIR}
for dir in `ls -d -1 *`
do
    pip install -r ${dir}/requirements.txt -t ${dir}/
done