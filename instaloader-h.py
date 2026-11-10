import instaloader
from itertools import islice
import os
import sys
import re
import argparse
import time
import json

RESULTS_FILE = "results_live.json"

def save_results(collected):
    """Write current results to JSON so the HTML page can poll it."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

import instaloader
from itertools import islice
import os
import sys
import re
import argparse
import time
import json

RESULTS_FILE = "results_live.json"

def save_results(collected):
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

def search_in_profile(L, username, keyword, max_posts, output_dir, collected):
    found = 0
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        for post in islice(posts, max_posts):
            caption = post.caption if post.caption else ""
            if re.search(rf"\b{re.escape(keyword)}\b", caption, re.IGNORECASE):
                found += 1
                print(f"  [MATCH] @{username} | {post.shortcode} | {post.date_utc}")

                # 1. Download the post
                L.download_post(post, target=output_dir)
                
                # 2. Ask Instaloader EXACTLY what the filename is
                # (This handles the date-based naming automatically)
                base_path = L.get_filename(post)
                
                # 3. Check for the image (handles .jpg or .webp)
                media_files = []
                for ext in [".jpg", ".webp"]:
                    # Instaloader puts the image next to the .txt file
                    file_path = f"{base_path}{ext}"
                    if os.path.exists(file_path):
                        # Make path relative for the browser (e.g. results_ps5/2026-09...jpg)
                        rel_path = f"{output_dir}/{os.path.basename(file_path)}"
                        media_files.append(rel_path)
                        break
                
                # Also check for video if it's a video post
                if post.is_video:
                    video_path = f"{base_path}.mp4"
                    if os.path.exists(video_path):
                        rel_path = f"{output_dir}/{os.path.basename(video_path)}"
                        media_files.append(rel_path)

                # 4. Save our custom text file
                txt_path = os.path.join(output_dir, f"{post.shortcode}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"Username: @{username}\n")
                    f.write(f"Shortcode: {post.shortcode}\n")
                    f.write(f"URL: https://www.instagram.com/p/{post.shortcode}/\n")
                    f.write(f"Date: {post.date_utc}\n")
                    f.write("-" * 40 + "\n")
                    f.write(caption)

                # 5. Save to JSON
                collected.append({
                    "username": username,
                    "shortcode": post.shortcode,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "date": str(post.date_utc),
                    "caption": caption,
                    "media_files": media_files,
                    "is_video": post.is_video,
                })
                save_results(collected)
                
                print(f"    -> Found media: {media_files}")

    except Exception as e:
        print(f"  [SKIP] @{username}: {e}")
    return found

# ... (The rest of your main() function remains exactly the same) ...

def main():
    parser = argparse.ArgumentParser(
        description="Search for a keyword in Instagram posts with live HTML results"
    )
    parser.add_argument("username", help="Target username (search source)")
    parser.add_argument("keyword", help="Keyword to search for")
    parser.add_argument("--source", choices=["single", "followers", "followees"], default="single")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--max-posts", type=int, default=30)
    parser.add_argument("--login-user", type=str, default=None)
    parser.add_argument("--session-file", type=str, default=None)
    args = parser.parse_args()

    output_dir = f"results_{args.keyword}"
    os.makedirs(output_dir, exist_ok=True)

    # reset live results file at start
    save_results([])

    L = instaloader.Instaloader(save_metadata=False)

    if args.source in ("followers", "followees"):
        if args.session_file:
            try:
                L.load_session_from_file(args.session_file)
                print(f"Loaded session for @{args.session_file}")
            except FileNotFoundError:
                print(f"Session file for @{args.session_file} not found.")
                print(f"Create it first: instaloader --login={args.session_file}")
                sys.exit(1)
        elif args.login_user:
            pw = input(f"Password for @{args.login_user}: ")
            L.login(args.login_user, pw)
            print(f"Logged in as @{args.login_user}")
        else:
            print("ERROR: followers/followees search requires login.")
            sys.exit(1)

    print(f"\nSearching '{args.keyword}' (source: {args.source})...\n")
    print("Open index.html in a browser to watch results appear live.\n")

    collected = []
    total_found = 0

    if args.source == "single":
        total_found = search_in_profile(L, args.username, args.keyword,
                                        args.max_posts, output_dir, collected)
    else:
        try:
            base_profile = instaloader.Profile.from_username(L.context, args.username)
        except Exception as e:
            print(f"Cannot load @{args.username}: {e}")
            sys.exit(1)

        if args.source == "followers":
            user_iter = base_profile.get_followers()
            desc = "followers"
        else:
            user_iter = base_profile.get_followees()
            desc = "following"

        count = 0
        for user_profile in user_iter:
            if count >= args.limit:
                break
            count += 1
            print(f"[{count}/{args.limit}] Checking @{user_profile.username} ({desc})...")
            total_found += search_in_profile(L, user_profile.username, args.keyword,
                                             args.max_posts, output_dir, collected)
            time.sleep(2)

    print(f"\nDone. Total {total_found} matching post(s) found.")
    print(f"Results saved in: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()