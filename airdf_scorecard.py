import requests
import sys
import re
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_repo_url(repo_url):
    """Validate repository URL format to prevent injection attacks."""
    pattern = r'^github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$'
    if not re.match(pattern, repo_url):
        raise ValueError("Invalid repository URL format. Use: github.com/owner/repo")
    return repo_url

def main():
    # run this with a terminal command: python airdf_scorecard.py github.com/pytorch/pytorch
    
    # Define the repository URL - use command line argument if provided, otherwise use environment variable or default
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
    else:
        repo_url = os.getenv('DEFAULT_REPO', 'github.com/torvalds/linux')
    
    try:
        # Validate the repository URL format
        repo_url = validate_repo_url(repo_url)
        logger.info(f"Checking scorecard for repository: {repo_url}")
        
        # Ensure HTTPS is used and construct the API URL (no URL encoding needed)
        scorecard_url = f"https://api.securityscorecards.dev/projects/{repo_url}"
        
        # Verify HTTPS is being used
        if not scorecard_url.startswith('https://'):
            raise ValueError("Only HTTPS URLs are allowed")
        
        # Make a call to the OpenSSF Scorecards API with timeout
        try:
            scorecard_response = requests.get(scorecard_url, timeout=30)
        except requests.exceptions.Timeout:
            logger.error("Request timed out after 30 seconds")
            sys.exit(1)
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - please check your internet connection")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            sys.exit(1)
        
        # Verify response headers for security
        if 'content-type' in scorecard_response.headers:
            if 'application/json' not in scorecard_response.headers['content-type']:
                logger.warning("Unexpected content type received")
        
        if scorecard_response.status_code == 200:
            try:
                scorecard_data = scorecard_response.json()
                logger.info("OpenSSF Scorecard data retrieved successfully!")
                print(f"Repository: {scorecard_data.get('repo', {}).get('name', 'N/A')}")
                print(f"Score: {scorecard_data.get('score', 'N/A')}")
            except requests.exceptions.JSONDecodeError:
                logger.error("Failed to parse JSON response from scorecard API")
                print(f"Response content: {scorecard_response.text[:200]}...")
        else:
            logger.error(f"Failed to retrieve scorecard data. Status code: {scorecard_response.status_code}")
            print(f"Failed to retrieve scorecard data. Status code: {scorecard_response.status_code}")
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
