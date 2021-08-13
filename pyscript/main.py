import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import json
import yaml
from rich.console import Console
from rich.table import Table
from nested_lookup import nested_lookup

console = Console()

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

    # status of helm charts
    print("\nStatus of helm charts\n")
    subprocess.run("helm list", shell =True)
    print("--" * 70)

    print("\nDEPLOYEMENT DETAILS\n")

    pp = subprocess.Popen(f"kubectl get service -o json {name}", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = pp.stdout.read()
    string = output.decode().replace("'", '"')
    _json = eval(string)

    table = Table(show_header=True)

    table.add_column("NAME")
    table.add_column("Type")
    table.add_column("CLUSTER-IP")
    table.add_column("EXTERNAL-IP")
    table.add_column("PORT(S)")

    tt = f'{_json["spec"]["ports"][0]["port"]}:{_json["spec"]["ports"][0]["nodePort"]}/{_json["spec"]["ports"][0]["protocol"]}'

    table.add_row(
        f'{_json["metadata"]["name"]}',
        f'{_json["spec"]["type"]}',
        f'{_json["spec"]["clusterIP"]}',
        f'{_json["status"]["loadBalancer"]}',
        tt
    )
    console.print(table)

if __name__ == "__main__":
    main()