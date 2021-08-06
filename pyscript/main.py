import os
import subprocess
import yaml
from kubernetes import client, config


def check_system_installations():
    try:
        subprocess.Popen(f"helm version",shell=True,stdout=subprocess.PIPE,).stdout.read()
        subprocess.Popen(f"kubectl version --client",shell=True,stdout=subprocess.PIPE,).stdout.read()
        subprocess.Popen(f"minikube version",shell=True,stdout=subprocess.PIPE,).stdout.read()

    except subprocess.CalledProcessError as e:
        print (e.output)


def parse_helm_chart(helm_path):
    values_file = os.path.join(helm_path,"Chart.yaml")
    with open(values_file, 'r') as f:
        doc = yaml.load(f)
    name_of_chart = doc['name']

    return name_of_chart

def main():

    check_system_installations()

    helm_location = input("Enter the location of helm chart:  ")
        
    name = parse_helm_chart(helm_location)
    subprocess.Popen(f"helm install {name} {helm_location}",shell=True,stdout=subprocess.PIPE,).communicate()

    config.load_kube_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
        (i.status.pod_ip, i.metadata.namespace, i.metadata.name ))
    
    #status of helm charts
    print("\nStatus of helm charts\n")
    subprocess.run("helm list", shell =True)

    print("\nListing services and its status\n")
    subprocess.run("kubectl get service", shell=True)

if __name__ == "__main__":
    main()