# photomaton-printer

### Example curl requests

curl -X POST http://localhost:5000/trigger-print -H "Content-Type: application/json" -d '{
"image_urls": ["https://oaidalleapiprodscus.blob.core.windows.net/private/org-t99RSKR5bW0lhuWQlHWow0LD/user-7Z1DWNis9zUxppWZ98L5fXw1/img-LTLAe7ghAw8sOWgWg7bTGOLp.png?st=2024-02-25T16%3A01%3A53Z&se=2024-02-25T18%3A01%3A53Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-02-24T22%3A33%3A11Z&ske=2024-02-25T22%3A33%3A11Z&sks=b&skv=2021-08-06&sig=z9iBEZwUQ%2BKYBKSeDa9yYWloizRyNSZJP1P4s3j96bo%3D"]
}'

curl -X GET http://localhost:5500/cut-paper
