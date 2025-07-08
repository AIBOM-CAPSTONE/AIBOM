import requests
import sys

response = requests.get('https://httpbin.org/ip')

print("Hello, World!")
print('Your IP is {0}'.format(response.json()['origin']))
print("Thanks for testing this out!")

# Define the repository URL - use command line argument if provided, otherwise default
if len(sys.argv) > 1:
    repo_url = sys.argv[1]
else:
    repo_url = "github.com/pytorch/pytorch"

print(f"Checking scorecard for repository: {repo_url}")

# Make a call to the OpenSSF Scorecards API
scorecard_url = f"https://api.securityscorecards.dev/projects/{repo_url}"
scorecard_response = requests.get(scorecard_url)

if scorecard_response.status_code == 200:
    try:
        scorecard_data = scorecard_response.json()
        print("OpenSSF Scorecard data retrieved successfully!")
        print(f"Repository: {scorecard_data.get('repo', {}).get('name', 'N/A')}")
        print(f"Score: {scorecard_data.get('score', 'N/A')}")
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response from scorecard API")
        print(f"Response content: {scorecard_response.text[:200]}...")
else:
    print(f"Failed to retrieve scorecard data. Status code: {scorecard_response.status_code}")
