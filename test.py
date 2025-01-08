import requests

# Your Notion API token (integration token)
NOTION_TOKEN = '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'

# Database ID (replace with your actual database ID)
# DATABASE_ID = '15ae4d6f-3fe2-8056-9012-dc52adec0553'

# Headers for the request
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",  # Specify the Notion API version
    "Content-Type": "application/json"
}

# Query parameters (optional, adjust based on your query needs)
query = {
  "object": "list",
  "results": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Week 1: Dec 02 - 08"
            }
          }
        ]
      }
    }
  ]
}


# Send the query request to the Notion API
response = requests.get(
    f'https://api.notion.com/v1/blocks/150e4d6f3fe2809fba1dee92663bad16/children',
    headers=headers,
    json=query
)

# Check if the request was successful
if response.status_code == 200:
    results = response.json()
    print("Results:", results)
else:
    print(f"Error: {response.status_code}, {response.text}")
