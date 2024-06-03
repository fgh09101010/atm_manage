import subprocess
m=("AtmAddress","AtmMain","City","Customer" ,"Transaction")
t=("atm_address","atm_main","atm_city","Customer" ,"Transaction")
for i in range(len(t)):
    command = "python manage.py dumpdata atm.model_name --format=yaml > yaml/table_name.yaml"
    command=command.replace("table_name",t[i]).replace("model_name",m[i])
    
    subprocess.run(command, shell=True, check=True)