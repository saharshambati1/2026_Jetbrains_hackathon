import os
import requests
import json
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GRID_API_KEY = os.getenv("GRID_API_KEY")
HOSTNAME = "api-op.grid.gg"
GRAPHQL_ENDPOINT = f"https://{HOSTNAME}/central-data/graphql"

class GridClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or GRID_API_KEY
        if not self.api_key:
            raise ValueError("GRID_API_KEY not found in environment variables")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # DNS Debug - Forcing IP Fallback due to persistent resolution errors
        # try:
        #     ip = socket.gethostbyname(HOSTNAME)
        #     print(f"DEBUG: Resolved {HOSTNAME} to {ip}")
        #     self.endpoint = GRAPHQL_ENDPOINT
        # except socket.gaierror:
        print(f"DEBUG: Forcing fallback IP for {HOSTNAME}.")
        # Fallback to hardcoded IP (from nslookup) if possible or fail
        # We will use one of the IPs found: 54.77.68.65
        self.fallback_ip = "54.77.68.65"
        self.endpoint = f"https://{self.fallback_ip}/central-data/graphql"
        self.headers["Host"] = HOSTNAME
        print(f"DEBUG: Using fallback IP {self.fallback_ip} with Host header.")

    def query(self, query_str, variables=None):
        payload = {"query": query_str, "variables": variables or {}}
        # Verify=False might be needed if using IP and SSL cert doesn't match IP (it won't).
        # We accept the risk for this hackathon demo.
        verify = True
        if "Host" in self.headers:
            verify = False 
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, verify=verify)
            if response.status_code == 200:
                result = response.json()
                if "errors" in result:
                    print("GraphQL Errors:", result["errors"])
                return result
            else:
                raise Exception(f"Query failed with status code {response.status_code}: {response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")

    def get_recent_valorant_series(self, limit=5):
        query = """
        query GetRecentSeries($limit: Int) {
          series(
            filter: { titleId: { eq: 2 } } 
            orderBy: START_DATE_DESC
            first: $limit
          ) {
            edges {
              node {
                id
                start
                end
                teams {
                  base {
                    name
                  }
                }
                tournament {
                  name
                }
              }
            }
          }
        }
        """
        return self.query(query, variables={"limit": limit})

    def get_all_titles(self):
        query = """
        query GetAllTitles {
          titles {
             id
             name
          }
        }
        """
        return self.query(query)

if __name__ == "__main__":
    try:
        client = GridClient()
        print("Fetching Titles...")
        titles = client.get_all_titles()
        print(json.dumps(titles, indent=2))
        
        print("\nFetching Recent Series...")
        series = client.get_recent_valorant_series()
        print(json.dumps(series, indent=2))
    except Exception as e:
        print(f"Error: {e}")
