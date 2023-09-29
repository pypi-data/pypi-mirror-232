# Async API wrapper for [TONIC.for Publishers Api V3](https://publisher.tonic.com/privileged/docs/api-documentation)

## How to use this package?

### Step #1 - Install Tonic API Client:

```pip install TonicPublisherAPI```

### Step #2 - create Client instance and use one of methods

```
from TonicPublisherAPI import TonicAPIClient

# Important - you need to initialize TonicAPIClient() inside async function because of aiohttp session,
that created on __init__() and used for all class methods to speedup network requests.

client = TonicAPIClient(your_consumer_key, your_consumer_password)

# Get campaigns list
...
await client.get_campaigns_list()
...

# Create new campaign
...
await client.create_campaign(
    name="New Campaign Name",
    offer="Educational Toys PR",
    country="US",
    offer_id="Offer ID",
    imprint="yes or no",
)
...

```

This package use `aiohttp` library to make requests to the Tonic Publishers API, so you need to use asynchronous programming style to create your business logic.

Example #1

```
import asyncio
from TonicPublisherAPI import TonicAPIClient

async def main():
    # Important - you need to initialize TonicAPIClient() inside async function
    # because of aiohttp session, that created on __init__() and used for all methods

    client = TonicAPIClient(your_consumer_key, your_consumer_password)
    
    campaigns = await client.get_campaigns_list(state="stopped", output="json") # Default state is "active"
    print(campaigns)
    
    # Important - you need to close session after all manipulations
    await client.close_session()

if __name__ == "__main__":
    asyncio.run(main())

```

Example #1 Output

```
[
  {
    "id": "1",
    "name": "First Campaign Test",
    "type": "display",
    "country": "US",
    "imprint": "no",
    "offer_id": "3",
    "offer": "Test Offer",
    "vertical": "Test Vertical",
    "link": "123456.track.com",
    "target": "test-target.bond"
  },
  {
    "id": "2",
    "name": "Second Campaign Test",
    "type": "display",
    "country": "US",
    "imprint": "no",
    "offer_id": "3",
    "offer": "Test Offer",
    "vertical": "Test Vertical",
    "link": "78901.track.com",
    "target": "test-target-2.bond"
  }
]
```

