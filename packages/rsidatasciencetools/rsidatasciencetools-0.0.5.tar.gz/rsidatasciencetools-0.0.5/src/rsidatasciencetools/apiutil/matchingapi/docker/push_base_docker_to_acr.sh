# add the file ~/.azure/acr.env to your linux workspace
# put the password to the ACR in this file with:
#       export AZURE_ACR_URL=devnextgen.azurecr.io  (e.g.)
#       export AZURE_ACR_PW=<password>
#       export AZURE_ACR_USER=<username>
if [[ -z "$AZURE_ACR_URL" ]]; then
    source ~/.azure/acr.env
fi

# echo "enter version tag: "
# read version

docker login $AZURE_ACR_URL -u $AZURE_ACR_USER -p $AZURE_ACR_PW

docker tag rsi.revx/base.ml_api rsi.revx/base.ml_api:latest 
docker tag rsi.revx/base.ml_api:latest $AZURE_ACR_URL/rsi.revx/base.ml_api
docker push $AZURE_ACR_URL/rsi.revx/base.ml_api

if [[ -z "$version" ]]; then
    exit 0
fi
if [ `echo "$version" | grep -c latest` -eq 0 ]; then
    # upload for this specific tag
    docker tag rsi.revx/base.ml_api:$version $AZURE_ACR_URL/rsi.revx/base.ml_api
    docker push $AZURE_ACR_URL/rsi.revx/base.ml_api
fi
