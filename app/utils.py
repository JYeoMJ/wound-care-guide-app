import os
import boto3
from botocore.exceptions import NoCredentialsError
import streamlit as st
import logging

#==============================================================================
# LOGGING CONFIGURATION
#==============================================================================
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#==============================================================================
# VIDEO PATH LOADING
#==============================================================================
def load_video_paths():
    """
    Load video paths either from local storage or S3 bucket
    Returns a dictionary of video references and their paths
    """
    # Check if we're using S3 or local storage
    use_s3 = os.environ.get('USE_S3', 'False').lower() == 'true'
    
    if use_s3:
        return load_videos_from_s3()
    else:
        return load_local_videos()

#------------------------------------------------------------------------------
# LOCAL VIDEO LOADING
#------------------------------------------------------------------------------
def load_local_videos():
    """Load videos from local storage"""
    videos = {}
    video_dir = os.path.join(os.path.dirname(__file__), 'static', 'videos')
    
    # Check if the directory exists
    if not os.path.exists(video_dir):
        logger.warning(f"Video directory does not exist: {video_dir}")
        os.makedirs(video_dir, exist_ok=True)
    
    # First try to find actual videos in the directory
    try:
        # Get all video files first
        video_files = []
        for filename in os.listdir(video_dir):
            if filename.lower().endswith(('.mp4', '.mov')):
                video_files.append(filename)
        
        # Sort files to prioritize mp4 over mov when both exist
        # This ensures mp4 will be processed last and take precedence
        video_files.sort(key=lambda x: '.mov' in x.lower())
        
        # Process sorted files
        for filename in video_files:
            base_name = os.path.splitext(filename)[0]  # Remove extension
            ext = os.path.splitext(filename)[1].lower()
            
            if base_name.startswith('video_'):
                # Extract reference from filename (e.g., video_2_1_1 → 2.1.1)
                ref = base_name.replace('video_', '').replace('_', '.')
                
                # If this reference already exists and current file is .mov, skip it
                # (This ensures mp4 is used if both exist)
                if ref in videos and ext == '.mov' and videos[ref].endswith('.mp4'):
                    logger.info(f"Skipping {filename} as MP4 version is already loaded")
                    continue
                
                videos[ref] = os.path.join(video_dir, filename)
                logger.info(f"Found local video for reference '{ref}': {filename}")
    except Exception as e:
        logger.error(f"Error scanning video directory: {str(e)}")
    
    # If no videos found or error occurred, fall back to placeholders
    if not videos:
        logger.info("No local videos found, using placeholders")
        # Default video references
        video_refs = [
            "2.1.1", "2.1.2", "2.2.1", "2.3", "2.4", "2.5",
            "3.1", "3.2", "3.3", "4.0", "5.0"
        ]
        
        for ref in video_refs:
            videos[ref] = os.path.join(video_dir, f"video_{ref.replace('.', '_')}.mp4")
    
    return videos

#------------------------------------------------------------------------------
# S3 VIDEO LOADING
#------------------------------------------------------------------------------
def load_videos_from_s3():
    """Load videos from S3 bucket"""
    videos = {}
    s3_videos = {}  # Temporary storage to sort by format
    
    try:
        # Get S3 configuration from environment variables
        s3_bucket = os.environ.get('S3_BUCKET_NAME')
        s3_prefix = os.environ.get('S3_PREFIX', 'videos/')
        region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Initialize S3 client
        s3 = boto3.client('s3', region_name=region)
        
        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
        
        # First collect all video objects
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                # Support both .mp4 and .mov file extensions
                if key.lower().endswith(('.mp4', '.mov')):
                    # Extract reference from filename
                    filename = os.path.basename(key)
                    base_name = os.path.splitext(filename)[0]  # Remove extension
                    ext = os.path.splitext(filename)[1].lower()
                    
                    # Extract reference number from the filename (e.g., video_2_1_1 → 2.1.1)
                    if base_name.startswith('video_'):
                        ref = base_name.replace('video_', '').replace('_', '.')
                        
                        # Store in temporary dictionary with format info
                        if ref not in s3_videos:
                            s3_videos[ref] = []
                        
                        s3_videos[ref].append({
                            'key': key,
                            'ext': ext,
                            'url': f"https://{s3_bucket}.s3.{region}.amazonaws.com/{key}"
                        })
        
        # Process collected videos with priority for MP4
        for ref, video_list in s3_videos.items():
            # Sort to prioritize .mp4 over .mov
            video_list.sort(key=lambda x: x['ext'] != '.mp4')
            
            # Use the first one after sorting (should be mp4 if available)
            selected_video = video_list[0]
            videos[ref] = selected_video['url']
            
            # Log the selected video and format
            logger.info(f"Using {selected_video['ext']} format for reference '{ref}': {os.path.basename(selected_video['key'])}")
            
            # Log if we skipped any alternates
            if len(video_list) > 1:
                skipped = [os.path.basename(v['key']) for v in video_list[1:]]
                logger.info(f"Skipped alternate formats for reference '{ref}': {', '.join(skipped)}")
        
        if not videos:
            logger.warning("No videos found in S3 bucket with the expected naming convention")
            
        return videos
    
    except NoCredentialsError:
        # Fall back to local if AWS credentials not found
        logger.error("AWS credentials not found")
        return load_local_videos()
    except Exception as e:
        # Fall back to local if any other error occurs
        logger.error(f"Error loading videos from S3: {str(e)}")
        return load_local_videos()

#==============================================================================
# VIDEO SEQUENCE DETERMINATION
#==============================================================================
def get_video_sequence(selections):
    """
    Determine the sequence of videos to display based on user selections
    
    Args:
        selections: List of dictionaries containing user selections
        
    Returns:
        List of dictionaries with video references and titles
    """
    sequence = []
    
    # Extract wound type from selections
    wound_type = next((s["type_of_wound"] for s in selections if "type_of_wound" in s), None)
    
    #------------------------------------------------------------------------------
    # SPECIAL CASE: DIRECT PATHS (webspace, multiple_toes, povidone)
    #------------------------------------------------------------------------------
    if wound_type in ["webspace", "multiple_toes", "povidone"]:
        # Get the video reference
        video_ref = next((s["video_ref"] for s in selections if "video_ref" in s), None)
        if video_ref:
            sequence.append({
                "ref": video_ref,
                "title": get_title_for_reference(video_ref)
            })
        
        # Add secondary dressing automatically
        sequence.append({
            "ref": "4.0",
            "title": "Tubifast to secure"
        })
        
        sequence.append({
            "ref": "5.0",
            "title": "Things to watch out for"
        })
        
        return sequence
    
    #------------------------------------------------------------------------------
    # NORMAL CASE: STEP-BY-STEP SELECTION
    #------------------------------------------------------------------------------
    # Process selections for superficial and cavity wounds
    for selection in selections:
        if "video_ref" in selection:
            sequence.append({
                "ref": selection["video_ref"],
                "title": get_title_for_reference(selection["video_ref"])
            })
    
    # Add Tubifast and watch out videos to all sequences
    sequence.append({
        "ref": "4.0",
        "title": "Tubifast to secure"
    })
    
    sequence.append({
        "ref": "5.0",
        "title": "Things to watch out for"
    })
    
    return sequence

#==============================================================================
# HELPER FUNCTIONS
#==============================================================================
def get_title_for_reference(ref):
    """Get a descriptive title for a video reference"""
    titles = {
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
    
    return titles.get(ref, f"Video {ref}")
