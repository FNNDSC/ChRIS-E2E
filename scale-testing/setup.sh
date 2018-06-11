sudo systemctl restart docker
#oc login https://openshift.massopen.cloud --token=4M29t7NSlcuMtVuX4YRta4hwRsXpfLdb50ZyR_5ymCg
sudo oc cluster up --skip-registry-check=true
sudo oc login -u system:admin --insecure-skip-tls-verify=true
sudo oc create sa robot -n myproject
sudo oc describe sa robot -n myproject
token="$(sudo oc describe sa robot)"
token=$(echo "$token" | grep -A 2 "Mountable secrets" | grep -v "Tokens: ")
token=$(echo "$token" | grep "robot-token-*")
token=$(echo "$token" | cut --delimiter=: --fields=2)
token=$(echo "$token" | tr -d '[:space:]')
sudo oc adm policy add-role-to-user edit system:serviceaccount:myproject:robot -n myproject
sudo oc describe secret $token -n myproject
token_val=$(sudo oc describe secret $token | grep "token: *" )
token_val=$(echo "$token_val" | cut -c 7- | sed -e 's/^[ \t]*//')
sudo mkdir /tmp/share
sudo chcon -R -t svirt_sandbox_file_t /tmp/share/
sudo oc patch scc restricted -p 'allowHostDirVolumePlugin: true'
sudo oc patch scc restricted -p '"runAsUser": {"type": "RunAsAny"}'
rm -f ~/.kube/config
oc login --token=$token_val --server=172.30.0.1:443 --insecure-skip-tls-verify=true
oc project myproject
oc create secret generic kubecfg --from-file=$HOME/.kube/config -n myproject
sudo sh -c 'printf "#pman_config\n[AUTH TOKENS]\npassword = password\n" > /home/ckaubisch/ChRIS-E2E/scale-testing/pman_config.cfg'
p_config="$(cat /home/ckaubisch/ChRIS-E2E/scale-testing/pman_config.cfg | base64)"
sudo sh -c 'printf "apiVersion: v1\nkind: Secret\nmetadata:\n    name: pman-config\ntype: Opaque\ndata:\n    pman_config.cfg: '$p_config'" > /etc/pman/auth/pman-secret.yml'
oc create -f /etc/pman/auth/pman-secret.yml
rm -f ~/.kube/config
oc login --username='developer' --password='developer' --server=localhost:8443 --insecure-skip-tls-verify=true

# To run with swift:

#oc create secret generic swift-credentials --from-file=/home/ckaubisch/etc/swift-credentials.cfg
#oc new-app pman-openshift-template-without-reaper.json
#oc set env dc/pman OPENSHIFTMGR_PROJECT=myproject

#oc new-app /home/ckaubisch/pfioh/openshift/pfioh-openshift-template.json

# to run without swift:

oc new-app /home/ckaubisch/pman/openshift/pman-openshift-template-without-swift.json
oc set env dc/pman OPENSHIFTMGR_PROJECT=myproject  
oc new-app /home/ckaubisch/pfioh/openshift/pfioh-openshift-template-without-swift.json

