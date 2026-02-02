
import os
import json
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

load_dotenv()

GRID_API_KEY = os.getenv("GRID_API_KEY")
CENTRAL_DATA_URL = "https://api-op.grid.gg/central-data/graphql"

def test_query():
    transport = RequestsHTTPTransport(
        url=CENTRAL_DATA_URL,
        headers={"x-api-key": GRID_API_KEY},
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Attempt to query games/matches inside a series
    # We'll use the Cloud9 ID: "79"
    query_str = """
    query TestSeriesDetails {
      allSeries(
        filter: { teamIds: { in: ["79"] } }, 
        first: 1, 
        orderBy: StartTimeScheduled, 
        orderDirection: DESC
      ) {
        edges {
          node {
            id
            startTimeScheduled
            matches {
              id
              games {
                  id
                  finished
                  map {
                      name
                  }
              }
            }
          }
        }
      }
    }
    """
    
    # Note: I am guessing 'matches' or 'games'. If this fails, I'll see the error.
    # Actually, often 'series' contains 'matches'.
    
    try:
        query = gql(query_str)
        result = client.execute(query)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")

    # Fallback attempt with 'games' directly if matches fails
    if "Cannot query field" in str(e) if 'e' in locals() else "":
         print("Retrying with 'games' instead of 'matches'...")
         query_str_2 = """
            query TestSeriesDetails2 {
              allSeries(
                filter: { teamIds: { in: ["79"] } }, 
                first: 1, 
                orderBy: StartTimeScheduled, 
                orderDirection: DESC
              ) {
                edges {
                  node {
                    id
                    games {
                        id
                    }
                  }
                }
              }
            }
         """
         try:
            query = gql(query_str_2)
            result = client.execute(query)
            print(json.dumps(result, indent=2))
         except Exception as e2:
            print(f"Error 2: {e2}")

if __name__ == "__main__":
    test_query()
