import os
import sys

def create_placeholder_files(format="mp4"):
    """
    Create placeholder text files to represent videos

    Args:
        format: File format to use for placeholders ("mp4" or "mov")
    """
    video_refs = [
        "2.1.1", "2.1.2", "2.2.1", "2.3", "2.4", "2.5",
        "3.1", "3.2", "3.3", "4.0", "5.0"
    ]

    video_titles = {
        "2.1.1": "Sheet Dressing Application",
        "2.1.2": "Iodosorb Powder/Gels Application",
        "2.2.1": "Primary Dressing for Cavity Wounds",
        "2.3": "Webspace Wound Treatment",
        "2.4": "Multiple Toe Wounds with Inadine",
        "2.5": "Wounds for Povidone Iodine Soaked Gauze",
        "3.1": "Toes Location Treatment",
        "3.2": "Mid Foot/Ankle Location Treatment",
        "3.3": "Heel Location Treatment",
        "4.0": "Tubifast to Secure",
        "5.0": "Things to Watch Out For"
    }

    # Path to the videos directory
    video_dir = os.path.join(os.path.dirname(__file__), 'static', 'videos')

    # Create the directory if it doesn't exist
    os.makedirs(video_dir, exist_ok=True)

    # Ensure format is valid
    if format.lower() not in ["mp4", "mov"]:
        print(f"Warning: Format '{format}' not recognized. Defaulting to mp4.")
        format = "mp4"

    # Create placeholder files for each video reference
    for ref in video_refs:
        filename = f"video_{ref.replace('.', '_')}.{format.lower()}"
        filepath = os.path.join(video_dir, filename)

        # Create an empty file
        with open(filepath, 'w') as f:
            f.write(f"Placeholder for {video_titles.get(ref, f'Video {ref}')}")

        print(f"Created placeholder: {filepath}")

    print("\nNOTE: These are placeholder files only. For actual deployment:")
    print(f"1. Replace them with real video files in {format.upper()} format")
    print("2. Keep the same naming convention: video_X_Y.mp4 (where X_Y is the reference number)")
    print("3. For S3 deployment, upload videos with the same naming convention to your bucket")
    print("4. Both .mp4 and .mov formats are supported by the application")

if __name__ == "__main__":
    # Check if format was specified as command line argument
    format = "mp4"
    if len(sys.argv) > 1 and sys.argv[1] in ["mp4", "mov"]:
        format = sys.argv[1]

    create_placeholder_files(format)
