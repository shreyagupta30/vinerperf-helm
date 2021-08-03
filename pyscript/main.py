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
        install()

def install():
    print("Installing Kubectl")
    subprocess.run('curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"', shell=True)
    subprocess.run('curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"', shell=True)
    subprocess.run('echo "$(<kubectl.sha256) kubectl" | sha256sum --check', shell=True)
    subprocess.run("sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl", shell=True)
    print("Installing minikube")
    subprocess.run("curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64", shell=True)
    subprocess.run("sudo install minikube-linux-amd64 /usr/local/bin/minikube")
    print("Installing Helm")
    subprocess.run("curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3", shell=True)
    subprocess.run("chmod 700 get_helm.sh", shell=True)
    subprocess.run("./get_helm.sh", shell=True)

def parse_kubernetes_config(file_path):
    config.load_kube_config(config_file = file_path)
    v1 = client.CoreV1Api()
    return v1

def parse_helm_chart(helm_path):
    values_file = os.path.join(helm_path,"Chart.yaml")
    with open(values_file, 'r') as f:
        doc = yaml.load(f)
    name_of_chart = doc['name']

    return name_of_chart


def main():
    check_system_installations()

    helm_location = input("Enter the location of helm chart:  ")
    config_k8_file = input("Enter the location of Kubernetes configuration file to be used(or press enter to pickup system defaults: ") or "~/.kube/config"
    
    v1 = parse_kubernetes_config(config_k8_file)
    name = parse_helm_chart(helm_location)

    subprocess.Popen(f"kubectl create namespace {name}",shell=True,stdout=subprocess.PIPE,).stdout.read()
    subprocess.Popen(f"helm install -f {os.path.join(helm_location, 'values.yaml')} -n {name} {name} {helm_location}",shell=True,stdout=subprocess.PIPE,).communicate()

    pod_list = v1.list_namespaced_pod(f"{name}")
    for pod in pod_list.items:
        print("%s\t%s\t%s\t%s\t%s" % (pod.metadata.name, pod.status.phase, pod.status.pod_i_ps, pod.status.host_ip, pod.status.conditions))

if __name__ == "__main__":
    main()