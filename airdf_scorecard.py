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
    pattern = r'^(github\.com|gitlab\.com)/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$'
    if not re.match(pattern, repo_url):
        raise ValueError("Invalid repository URL format. Use: github.com/owner/repo")
    return repo_url

def display_scorecard_data(scorecard_data):
    """Display comprehensive scorecard data including all checks and details."""
    
    # Display metadata
    print("\n" + "="*60)
    print("OPENSSF SCORECARD RESULTS")
    print("="*60)
    
    # Repository and analysis info. Note that the scorecard data is a JSON object, so we can access the data using the get method. The URL must be sent with / forward slashes, not endcoded as %2F.
    print(f"Repository: {scorecard_data.get('repo', {}).get('name', 'N/A')}")
    print(f"Analysis Date: {scorecard_data.get('date', 'N/A')}")
    print(f"Repository Commit: {scorecard_data.get('repo', {}).get('commit', 'N/A')}")
    print(f"Scorecard Version: {scorecard_data.get('scorecard', {}).get('version', 'N/A')}")
    print(f"Scorecard Commit: {scorecard_data.get('scorecard', {}).get('commit', 'N/A')}")
    print(f"Overall Score: {scorecard_data.get('score', 'N/A')}/10")
    
    # Display all checks
    checks = scorecard_data.get('checks', [])
    if checks:
        print(f"\nSecurity Checks ({len(checks)} total):")
        print("-" * 60)
        
        for i, check in enumerate(checks, 1):
            name = check.get('name', 'Unknown')
            score = check.get('score', 'N/A')
            reason = check.get('reason', 'No reason provided')
            
            # Format score display
            if score == -1:
                score_display = "N/A"
            else:
                score_display = f"{score}/10"
            
            print(f"\n{i}. {name}")
            print(f"   Score: {score_display}")
            print(f"   Reason: {reason}")
            
            # Display details if available
            details = check.get('details')
            if details:
                print("   Details:")
                for detail in details:
                    print(f"     • {detail}")
            
            # Display documentation
            doc = check.get('documentation', {})
            if doc:
                print(f"   Description: {doc.get('short', 'No description')}")
                print(f"   Documentation: {doc.get('url', 'No URL')}")
    
    print("\n" + "="*60)

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
                
                # Display comprehensive scorecard data
                display_scorecard_data(scorecard_data)
                
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
