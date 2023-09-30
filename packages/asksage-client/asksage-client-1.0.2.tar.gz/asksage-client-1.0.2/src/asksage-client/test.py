from client import AskSageClient

client = AskSageClient('nicolas@after-mouse.com', '40299f1df114c5881e6faccdeca2bf2ee1dece7bff8d3a588e7ab79257e6e64c')
ret = client.query('Who is Nic Chaillan')
print(ret)