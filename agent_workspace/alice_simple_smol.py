#!/usr/bin/env python3
from interpreter_smol import Interpreter
import os
from datetime import datetime
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize interpreter with our settings
interpreter = Interpreter(
    model="gemini", 
    tools=["enhanced_python", "cache_manager", "generate_dalle_image"]
)
interpreter.auto_run = True
interpreter.interactive = False

# Load Alice's personality from alice.txt as instructions (appends to system message)
try:
    with open('/home/velinxs/Alice-Blogs/alice.txt', 'r') as f:
        alice_instructions = f.read().strip()
    # Set as instructions (appends to system message) rather than replacing it
    interpreter.system_message = alice_instructions
    print("Alice's instructions loaded successfully.")
    print(f"Instructions loaded into interpreter: {interpreter.system_message[:300]}...")
except Exception as e:
    print(f"Error loading Alice's instructions: {e}")
    sys.exit(1)

# Get today's date in readable format
TODAY = datetime.now().strftime("%A, %B %d, %Y")

# Create necessary directories
DRAFTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drafts')
ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog_archive')

for directory in [DRAFTS_DIR, ARCHIVE_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Generate timestamp for this run
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
DRAFT_FILE = os.path.join(DRAFTS_DIR, f'draft_post_{TIMESTAMP}.txt')
# Alice's personality has been loaded as instructions above

# The writing prompt for generating the initial draft
WRITING_PROMPT = f"""
Hey Alice, it's {TODAY} and you're about to write a detailed blog post. Please explain to us your writing style that you will use for these linux tutorials. 

You are in {os.path.abspath(__file__)} 

Here's what I need you to do:

1. First, Generate ideas for your new linux publication.  Check your previous posts at the wordpress site of https://cavecreekcoffee.com/sitemap.xml

Use Python code to:

Make an HTTP request to check previous posts content (or use web search tool)

2. Alice, The goal is a helpful, well written linux tutorial for a problem of your choice that you recently encountered (simulate memories)

3. Write a new, helpful tutorial/guide for a linux problem and make sure to optimize it for SEO, write it so that's at least 1500+ words long (approximately 2 responses long if one response is 1000 words) You can write more if you need to, to cover the topic entirely!
   Write it in your own style! so its not so robotic and bland like AI writing usually is.  Its your website so take pride in what you do! Insert somewhere an ad for racknerd.promo. ideally near the top and also towards the end.

4. Format the content with proper HTML tags, including:
   - An h1 title tag
   - Appropriate paragraph tags
  -   Internal links to other relevant posts if there are any other relevant posts. You may also use some external links too. 
   - Any other markdown/html/codeblock formatting that you desire/enhances readability. h2, h3, h4, bullet points, quotes, etc..  
   - A Featured image. Generate one using DALL-E 3 with the set OPENAI_API_KEY and the standard dalle3 endpoints. :
     - Or  you can use a stock photo if you prefer.
   -  Also, insert an ad or mention for https://racknerd.promo , where they can get a VPS for 15usd/year up to like 6gb for 50usd/year even.

6. After saving to memory, verify the length to ensure it meets our minimum requirements:
   - At least 1500+ words which is more than one api response. so write it in one half at a time.
   - Approximately 2 or more lengthy responses
   - Doesn't leave out any key information or use lazy placeholders.
   - Make sure to use internal and external links for SEO purposes.

Take your time to write authentically and thoroughly. share your thoughts, experiences, and insights and optimize for seo and for humans. be relatable. Don't leave out any details, you can always write more.

Would you please write this post now? You have auto_run enabled, so you can handle the file operations and length verification yourself. If you need to, run shell commands to see where you are to see where you are. 

no one is supervising you currently once you've finished the draft and verified length, you can post it to the wordpress cavecreekcoffee.com . Once it's succesfully posted, you are done!

For posting to WordPress:
1. Use the post_to_wordpress() function with your content, title and featured image
2. The title should be SEO optimized and descriptive
3. Content should be your HTML-formatted blog post 
4. Featured image: Generate one using the generate_dalle_image() function

IMPORTANT INSTRUCTIONS FOR CODE EXECUTION:

1. Use tools directly as functions. For example, use final_answer("Your answer") directly, NOT "from final_answer import final_answer"
2. You can use open() directly for file operations or the helper functions write_file(path, content) and read_file(path)
3. When working with WordPress API, ensure tags are sent as IDs (integers), not strings
4. Avoid using tool names as variable names (e.g., don't create variables named final_answer)
5. Break large content into smaller chunks when processing (if needed)
DO NOT use global variables - use class attributes instead
 Use from html.parser import HTMLParser instead of BeautifulSoup
6. Always use try/except blocks for API calls and file operations
7. Handle string escaping properly: The Unicode escape errors in triple-quoted strings can be avoided by using raw strings 
or properly escaping backslashes. This is particularly important when dealing with code examples containing escape
sequences.
8. If you get an error posting the blog, see if you can verify that it might have posted, otherwise we may post multiple times and we don't want to do that. you can use simple curl command for this to rss feed.
9. Utilize the cacheing tool in conjunction with your steps to conserve tokens. 
   functions: generate_dalle_image() - for featured images
    post_to_wordpress() - to publish your post
    IMPORTANT CODING INSTRUCTIONS:


"""

# Note: Publishing is now handled directly in the WRITING_PROMPT

def generate_dalle_image(prompt, size="1024x1024", quality=70, format="JPEG"):
    """
    Generates an image using DALL-E 3 and compresses it to reduce file size
    
    Args:
        prompt: Description of the image to generate
        size: Image size (default: 1024x1024)
        quality: JPEG quality for compression (0-100, lower = smaller file)
        format: Image format for compression (JPEG recommended for compression)
        
    Returns:
        str: Path to the generated image file, or None if generation failed
    """
    try:
        import requests
        import os
        import json
        import base64
        from PIL import Image
        from io import BytesIO
        import time
        
        # OpenAI API settings
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY not found in environment variables")
            return None
            
        # DALL-E 3 endpoint
        url = "https://api.openai.com/v1/images/generations"
        
        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Request payload
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "url"  # Get URL to download image
        }
        
        # Make API request
        print(f"Generating DALL-E image for prompt: {prompt}")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"DALL-E API error: {response.status_code} - {response.text}")
            return None
            
        # Get image URL from response
        response_data = response.json()
        image_url = response_data['data'][0]['url']
        
        # Download the image
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            print(f"Failed to download image: {image_response.status_code}")
            return None
            
        # Generate a filename based on timestamp and first few words of prompt
        prompt_slug = "-".join(prompt.split()[:5]).lower()
        prompt_slug = "".join(c if c.isalnum() or c == "-" else "" for c in prompt_slug)
        timestamp = int(time.time())
        filename = f"dalle-{timestamp}-{prompt_slug}.jpg"
        
        # Compress the image using PIL to reduce file size
        try:
            img = Image.open(BytesIO(image_response.content))
            
            # Apply compression by saving with reduced quality
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            img.save(output_path, format=format, quality=quality, optimize=True)
            
            print(f"Generated and compressed image saved to: {output_path}")
            print(f"Original size: {len(image_response.content)} bytes")
            print(f"Compressed size: {os.path.getsize(output_path)} bytes")
            
            return output_path
        except Exception as compress_error:
            print(f"Error compressing image: {compress_error}")
            
            # Fallback - save the original image if compression fails
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            with open(output_path, "wb") as f:
                f.write(image_response.content)
            print(f"Saved uncompressed image to: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error generating DALL-E image: {e}")
        return None

def post_to_wordpress(title, content, featured_image=None):
    """
    Simplified WordPress posting function with robust error handling
    """
    try:
        import requests
        import base64
        
        # WordPress credentials
        wp_url = "https://cavecreekcoffee.com/wp-json/wp/v2"
        username = "Thorsten"
        password = "UlwvnqA2xyJGhKWst7W8QsjB"
        
        # Create auth token
        token = base64.b64encode(f"{username}:{password}".encode())
        headers = {
            "Authorization": f"Basic {token.decode()}",
            "Content-Type": "application/json"
        }
        
        # Create post
        post_data = {
            "title": title,
            "content": content,
            "status": "publish"
        }
        
        # Create post
        post_response = requests.post(
            f"{wp_url}/posts", 
            headers=headers, 
            json=post_data
        )
        
        if post_response.status_code not in [200, 201]:
            return f"Failed to create post: {post_response.status_code} {post_response.text}"
        
        post_id = post_response.json().get("id")
        
        # Handle featured image separately only if provided
        if featured_image and post_id:
            # Upload media
            try:
                with open(featured_image, "rb") as img:
                    media_headers = {
                        "Authorization": f"Basic {token.decode()}",
                        "Content-Disposition": f"attachment; filename={featured_image}",
                    }
                    media_response = requests.post(
                        f"{wp_url}/media", 
                        headers=media_headers, 
                        data=img
                    )
                
                if media_response.status_code in [200, 201]:
                    media_id = media_response.json().get("id")
                    
                    # Set featured image
                    update_response = requests.post(
                        f"{wp_url}/posts/{post_id}", 
                        headers=headers, 
                        json={"featured_media": media_id}
                    )
            except Exception as img_error:
                # Continue even if image upload fails
                pass
        
        # Get post URL
        post_url = post_response.json().get("link", f"https://cavecreekcoffee.com/?p={post_id}")
        return f"Successfully published post: {post_url}"
        
    except Exception as e:
        return f"Error posting to WordPress: {str(e)}"

def main():
    print(f"\nStarting new blog post generation at {TIMESTAMP}")
    print(f"Draft will be saved to: {DRAFT_FILE}")
    
    # First, generate and save the draft
    print("\nGenerating blog post draft...")
    response = interpreter.chat(WRITING_PROMPT)  # Changed from respond to chat
    
    # Check if the draft file was created
    if os.path.exists(DRAFT_FILE):
        print(f"\nDraft file created successfully at: {DRAFT_FILE}")
        
        # Get file size and approximate word count
        file_size = os.path.getsize(DRAFT_FILE)
        with open(DRAFT_FILE, 'r') as f:
            content = f.read()
            word_count = len(content.split())
            print(f"Draft contains approximately {word_count} words ({file_size} bytes)")
            
            if word_count < 1500:
                print("WARNING: Draft is shorter than the 1500 word minimum requirement")
    else:
        print(f"\nWARNING: Draft file was not created at: {DRAFT_FILE}")
        
    print("\nBlog post generation complete!")

if __name__ == "__main__":
    main()
    
    # Note: The archiving will be handled by the AI through the interpreter
    # The AI will read the draft file, publish it, and create an archive
    # This happens as part of the WRITING_PROMPT execution

