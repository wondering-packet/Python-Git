# Instructions to Set Up a Webhook in MS Teams to Receive Alerts from Python's `requests` Module

1.  **Create a team (or use existing one)**
    * Create a channel (or use existing one)

2.  **Teams > Workflows > Create from blank**
    * Search for "webhook"
    * Select "When a Teams webhook request is received"
    * **New step**
    * Search for "Parse JSON"
    * Paste in the following schema:
        ```json
        {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string"
                }
            }
        }
        ```
    * **Add step**
    * Search for "Post message in a chat or channel"
    * Select the desired values from "Post in", "Team" & "Channel" dropdowns
    * In the "message" body, paste in the following:
        ```
        @{triggerBody()?['text']}
        ```
    * **Save**
    * Test from 099-C script