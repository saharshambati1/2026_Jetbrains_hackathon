import os
import json
from dotenv import load_dotenv
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Load environment variables
load_dotenv()

GRID_API_KEY = os.getenv("GRID_API_KEY")
CENTRAL_DATA_URL = "https://api-op.grid.gg/central-data/graphql"
STATISTICS_FEED_URL = "https://api-op.grid.gg/statistics-feed/graphql"

class GridClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or GRID_API_KEY
        if not self.api_key:
            raise ValueError("GRID_API_KEY not found in environment variables")
        
        self.headers = {
            "x-api-key": self.api_key,
        }
        
        # Initialize clients for both endpoints
        self.central_client = self._create_client(CENTRAL_DATA_URL)
        self.stats_client = self._create_client(STATISTICS_FEED_URL)

    def _create_client(self, url):
        transport = RequestsHTTPTransport(
            url=url,
            headers=self.headers,
            use_json=True,
        )
        return Client(transport=transport, fetch_schema_from_transport=False)

    def execute_query(self, client_type, query_str, variables=None):
        client = self.central_client if client_type == "central" else self.stats_client
        query = gql(query_str)
        try:
            result = client.execute(query, variable_values=variables)
            return result
        except Exception as e:
            print(f"Error executing {client_type} query: {e}")
            return None

    def get_tournaments(self, first=5):
        query = """
        query GetTournaments($first: Int) {
          tournaments(first: $first) {
            edges {
              node {
                id
                name
              }
            }
          }
        }
        """
        data = self.execute_query("central", query, {"first": first})
        print("\n--- TOURNAMENT DATA ---")
        print(json.dumps(data, indent=2))
        return data

    def get_series(self, title_id=2, first=5):
        # Fallback to basic Series data as 'matches'/'games' fields are not exposed in this schema variant.
        query = """
        query GetSeries($titleId: ID!, $first: Int) {
          allSeries(
            filter: { titleIds: { in: [$titleId] } }, 
            first: $first, 
            orderBy: StartTimeScheduled, 
            orderDirection: DESC
          ) {
            edges {
              node {
                id
                startTimeScheduled
                teams {
                   baseInfo {
                     name
                     id
                   }
                }
              }
            }
          }
        }
        """
        data = self.execute_query("central", query, {"titleId": str(title_id), "first": first})
        print("\n--- SERIES DATA (via allSeries) ---")
        if data:
            # print(json.dumps(data, indent=2))
            pass
        return data

    def get_teams(self, first=5):
        query = """
        query GetTeams($first: Int) {
          teams(first: $first) {
            edges {
              node {
                id
                name
              }
            }
          }
        }
        """
        data = self.execute_query("central", query, {"first": first})
        print("\n--- TEAM DATA ---")
        print(json.dumps(data, indent=2))
        return data

    def get_players(self, first=5):
        # Using nickname as per introspection. Removed fullName due to permission error.
        query = """
        query GetPlayers($first: Int) {
          players(first: $first) {
            edges {
              node {
                id
                nickname
              }
            }
          }
        }
        """
        data = self.execute_query("central", query, {"first": first})
        print("\n--- PLAYER DATA ---")
        print(json.dumps(data, indent=2))
        return data

    def get_player_stats(self, player_id, title_id=2):
        """
        Fetches player statistics from the Statistics Feed.
        """
        query = """
        query GetPlayerStats($playerId: ID!) {
          playerStatistics(playerId: $playerId, filter: { startedAt: { period: LAST_MONTH } }) {
            series {
              kills { sum avg ratePerMinute { avg } }
              deaths { sum avg ratePerMinute { avg } }
              won { count }
            }
            game {
              kills { sum avg }
              deaths { sum avg }
            }
          }
        }
        """
        data = self.execute_query("stats", query, {"playerId": str(player_id)})
        print(f"\n--- PLAYER STATISTICS DATA (ID: {player_id}) ---")
        return data

    def get_team_stats(self, team_id):
        """
        Fetches team statistics from the Statistics Feed.
        """
        query = """
        query GetTeamStats($teamId: ID!) {
          teamStatistics(teamId: $teamId, filter: { startedAt: { period: LAST_MONTH } }) {
            series {
              kills { sum avg }
              deaths { sum avg }
            }
          }
        }
        """
        data = self.execute_query("stats", query, {"teamId": str(team_id)})
        print(f"\n--- TEAM STATISTICS DATA (ID: {team_id}) ---")
        # print(json.dumps(data, indent=2))
        return data

# Constants for Cloud9
CLOUD9_TEAM_ID = "79"
CLOUD9_ROSTER = {
    "OXY": "10636",
    "vanity": "91",
    "Xeppaa": "1193",
    "moose": "725",
    "v1c": "10612"
}

def save_to_json(data, filename="cloud9_dynamic_report.json"):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n[SUCCESS] Data saved to {filename}")

if __name__ == "__main__":
    client = GridClient()
    report = {
        "timestamp": "2026-02-01T10:45:00Z",
        "team_info": {},
        "recent_series": [],
        "roster_stats": {},
        "map_stats": {}
    }
    
    print("\n=== CLOUD9 DYNAMIC DATA REPORT ===")
    
    # 1. Team Context
    try:
        team_data = client.execute_query("central", """
        query GetC9($id: ID!) { team(id: $id) { id name } }
        """, {"id": CLOUD9_TEAM_ID})
        if team_data: report["team_info"] = team_data
    except: pass
    
    # 2. Recent Series (Detailed)
    try:
        series_res = client.get_series(title_id=2, first=5)
        if series_res:
            report["recent_series"] = series_res.get('allSeries', {}).get('edges', [])
        else:
            print("Warning: No series data returned.")
    except Exception as e:
        print(f"Failed to fetch detailed series data: {e}")
    
    # 3. Roster-Wide Stats (Last Year)
    print("\n[STEP 3] Fetching Statistics for the full Cloud9 Roster...")
    
    for nickname, p_id in CLOUD9_ROSTER.items():
        print(f" -> Fetching stats for {nickname}...")
        try:
            stats = client.get_player_stats(p_id)
            if stats: report["roster_stats"][nickname] = stats
        except Exception as e:
             print(f"Failed to fetch stats for {nickname}: {e}")
        
    # 4. Team-Level Combined Stats
    print("\n[STEP 4] Fetching Team-Level Statistics...")
    try:
        t_stats = client.get_team_stats(CLOUD9_TEAM_ID)
        if t_stats: report["team_stats"] = t_stats
    except: pass
    
    # 5. Save and Show
    save_to_json(report)
    print("\n--- FINAL CLOUD9 ROSTER SUMMARY (Sample: OXY) ---")
    if "OXY" in report["roster_stats"]:
        print(json.dumps(report["roster_stats"]["OXY"], indent=2))
