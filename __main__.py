import sys
import argparse
from google import genai
from google.genai.types import HttpOptions

def main():
    parser = argparse.ArgumentParser(description="Send a prompt and codebase context to Gemini.")
    parser.add_argument("--prompt", required=True, help="The prompt to insert into <user_request>")
    parser.add_argument("--dry-run", action="store_true", help="Output the built prompt without calling the API")
    args = parser.parse_args()

    # Check if data is being piped into stdin
    if sys.stdin.isatty():
        print("Error: Please pipe the output of the 'context' command into this script.")
        print("Example: context | python __main__.py --prompt 'your prompt'")
        sys.exit(1)
        
    codebase_context = sys.stdin.read()

    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print("Error: prompt.txt not found.")
        sys.exit(1)

    # Replace the empty tags with the tags containing the actual content
    modified_prompt = template.replace(
        "<user_request>\n\n</user_request>", 
        f"<user_request>\n{args.prompt}\n</user_request>"
    )
    
    modified_prompt = modified_prompt.replace(
        "<codebase>\n\n</codebase>", 
        f"<codebase>\n{codebase_context}\n</codebase>"
    )

    if args.dry_run:
        print(modified_prompt)
        sys.exit(0)

    client = genai.Client(
        vertexai=True,
        project="coder-470",
        location="us-central1",
        http_options=HttpOptions(api_version="v1")
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=modified_prompt,
    )

    print(response.text)

if __name__ == "__main__":
    main()
