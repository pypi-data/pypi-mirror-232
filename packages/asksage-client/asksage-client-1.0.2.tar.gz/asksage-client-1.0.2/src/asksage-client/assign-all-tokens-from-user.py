import json
from client import AskSageClient

client = AskSageClient('nicolas@after-mouse.com', '40299f1df114c5881e6faccdeca2bf2ee1dece7bff8d3a588e7ab79257e6e64c')
ret = client.query('/superadmin-get-dataset tom.brazil@icsinc.com')

message = ret['message']
if message[0] == '"':
    message = message[1:]
if message[-1] == '"':
    message = message[:-1]

assign_to = 'dany.strakos@icsinc.com'

array_datasets = json.loads(message)
for dataset in array_datasets:
    print('Assigning Dataset: ' + dataset)
    ret = client.query('/superadmin-assign-dataset ' + dataset + ' ' + assign_to)
    print(ret)