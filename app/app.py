import streamlit as st
import os
import boto3
from botocore.exceptions import NoCredentialsError
from utils import load_video_paths, get_video_sequence

#==============================================================================
# APPLICATION CONFIGURATION
#==============================================================================

# Configure page
st.set_page_config(
    page_title="Wound Care Guide",
    page_icon="🩹",
    layout="wide"
)

#==============================================================================
# SESSION STATE INITIALIZATION
#==============================================================================
# Initialize session state variables to track user progress through the flow
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'start'
    st.session_state.selected_videos = []
    st.session_state.video_sequence = []

#==============================================================================
# MAIN INTERFACE HEADER
#==============================================================================
# Title
st.title("Wound Care Video Guide System")
st.markdown("---")

#==============================================================================
# VIDEO RESOURCE LOADING
#==============================================================================
# Load video paths (either from local storage or S3 bucket)
videos = load_video_paths()

#==============================================================================
# SIDEBAR NAVIGATION
#==============================================================================
with st.sidebar:
    st.header("Navigation")
    
    # Reset button to start over
    if st.button("Restart Guide"):
        st.session_state.current_step = 'start'
        st.session_state.selected_videos = []
        st.session_state.video_sequence = []
        st.rerun()
    
    # Back button (only shown when not at start)
    if st.session_state.current_step != 'start':
        if st.button("Back to Previous Step"):
            if len(st.session_state.selected_videos) > 0:
                # Remove the last selection
                st.session_state.selected_videos.pop()
                
                # Reset to start if no selections remain
                if len(st.session_state.selected_videos) == 0:
                    st.session_state.current_step = 'start'
                else:
                    # Otherwise set appropriate step based on the last remaining selection
                    last_selection = st.session_state.selected_videos[-1]
                    if "type_of_wound" in last_selection:
                        st.session_state.current_step = 'type_selection'
                    elif "location" in last_selection:
                        st.session_state.current_step = 'location_selection'
                    elif "dressing" in last_selection:
                        st.session_state.current_step = 'dressing_selection'
                
                # Refresh the page with the new state
                st.rerun()
    
    # About section with app description
    st.header("About")
    st.info("""
    This application guides healthcare providers through wound care procedures
    based on wound type, location, and appropriate dressing techniques.
    
    Select options as prompted to view the appropriate instructional videos.
    """)

#==============================================================================
# DECISION TREE FLOW LOGIC
#==============================================================================

#------------------------------------------------------------------------------
# STEP 1: WOUND TYPE SELECTION
#------------------------------------------------------------------------------
if st.session_state.current_step == 'start':
    st.header("Select Type of Wound")
    
    # Create two columns for the wound type buttons
    wound_type_col1, wound_type_col2 = st.columns(2)
    
    # First column of wound type options
    with wound_type_col1:
        # Option 1: Superficial Wound
        if st.button("Superficial Wound", use_container_width=True):
            st.session_state.selected_videos.append({"type_of_wound": "superficial"})
            st.session_state.current_step = 'location_selection'
            st.rerun()
        
        # Option 2: Cavity/Concave Wound
        if st.button("Cavity/Concave Wound", use_container_width=True):
            st.session_state.selected_videos.append({"type_of_wound": "cavity"})
            st.session_state.current_step = 'location_selection'
            st.rerun()
    
    # Second column of wound type options
    with wound_type_col2:
        # Option 3: Webspace Wound (direct path)
        if st.button("Webspace Wound", use_container_width=True):
            st.session_state.selected_videos.append({"type_of_wound": "webspace", "video_ref": "2.3"})
            st.session_state.current_step = 'final'
            st.rerun()
        
        # Option 4: Multiple toe wounds (direct path)
        if st.button("Multiple toe wounds with inadine", use_container_width=True):
            st.session_state.selected_videos.append({"type_of_wound": "multiple_toes", "video_ref": "2.4"})
            st.session_state.current_step = 'final'
            st.rerun()
        
        # Option 5: Povidone iodine wounds (direct path)
        if st.button("Wounds for povidone iodine soaked gauze", use_container_width=True):
            st.session_state.selected_videos.append({"type_of_wound": "povidone", "video_ref": "2.5"})
            st.session_state.current_step = 'final'
            st.rerun()

#------------------------------------------------------------------------------
# STEP 2: WOUND LOCATION SELECTION
#------------------------------------------------------------------------------
# Only shown for superficial and cavity wounds
elif st.session_state.current_step == 'location_selection':
    st.header("Select Location of Wound")
    
    # Display the previously selected wound type
    wound_type = st.session_state.selected_videos[0]["type_of_wound"]
    st.subheader(f"Selected Wound Type: {wound_type.replace('_', ' ').title()}")
    
    # Create three columns for location options
    location_col1, location_col2, location_col3 = st.columns(3)
    
    # First column: Toes location
    with location_col1:
        if st.button("Toes", use_container_width=True):
            st.session_state.selected_videos.append({"location": "toes", "video_ref": "3.1"})
            # Different next step based on wound type
            if wound_type == "superficial":
                st.session_state.current_step = 'primary_dressing'
            else:  # cavity
                st.session_state.current_step = 'cavity_dressing'
            st.rerun()
    
    # Second column: Mid foot/ankle location
    with location_col2:
        if st.button("Mid foot/ankle", use_container_width=True):
            st.session_state.selected_videos.append({"location": "midfoot", "video_ref": "3.2"})
            # Different next step based on wound type
            if wound_type == "superficial":
                st.session_state.current_step = 'primary_dressing'
            else:  # cavity
                st.session_state.current_step = 'cavity_dressing'
            st.rerun()
    
    # Third column: Heel location
    with location_col3:
        if st.button("Heel", use_container_width=True):
            st.session_state.selected_videos.append({"location": "heel", "video_ref": "3.3"})
            # Different next step based on wound type
            if wound_type == "superficial":
                st.session_state.current_step = 'primary_dressing'
            else:  # cavity
                st.session_state.current_step = 'cavity_dressing'
            st.rerun()

#------------------------------------------------------------------------------
# STEP 3A: PRIMARY DRESSING SELECTION (FOR SUPERFICIAL WOUNDS)
#------------------------------------------------------------------------------
elif st.session_state.current_step == 'primary_dressing':
    st.header("Select Type of Primary Dressing")
    
    # Display previously selected options
    wound_type = st.session_state.selected_videos[0]["type_of_wound"]
    location = st.session_state.selected_videos[1]["location"]
    
    st.subheader(f"Selected Wound: {wound_type.replace('_', ' ').title()} wound at {location.replace('_', ' ').title()}")
    
    # Create two columns for dressing options
    dressing_col1, dressing_col2 = st.columns(2)
    
    # First column: Sheet dressing option
    with dressing_col1:
        if st.button("Sheet dressing", use_container_width=True):
            st.session_state.selected_videos.append({"dressing": "sheet", "video_ref": "2.1.1"})
            st.session_state.current_step = 'final'
            st.rerun()
    
    # Second column: Iodosorb powder/Gels option
    with dressing_col2:
        if st.button("Iodosorb powder/Gels", use_container_width=True):
            st.session_state.selected_videos.append({"dressing": "iodosorb", "video_ref": "2.1.2"})
            st.session_state.current_step = 'final'
            st.rerun()

#------------------------------------------------------------------------------
# STEP 3B: CAVITY WOUND TREATMENT (FOR CAVITY WOUNDS)
#------------------------------------------------------------------------------
elif st.session_state.current_step == 'cavity_dressing':
    st.header("Cavity Wound Treatment")
    
    # Display previously selected options
    wound_type = st.session_state.selected_videos[0]["type_of_wound"]
    location = st.session_state.selected_videos[1]["location"]
    
    st.subheader(f"Selected Wound: {wound_type.replace('_', ' ').title()} wound at {location.replace('_', ' ').title()}")
    
    st.info("For cavity/concave wounds, cut dressing to conform to wound shape")
    
    # Single option for cavity wounds
    if st.button("Primary Dressing for Cavity Wounds"):
        st.session_state.selected_videos.append({"dressing": "cavity_primary", "video_ref": "2.2.1"})
        st.session_state.current_step = 'final'
        st.rerun()

#------------------------------------------------------------------------------
# FINAL STEP: VIDEO SEQUENCE DISPLAY
#------------------------------------------------------------------------------
elif st.session_state.current_step == 'final':
    # Determine the complete video sequence based on all selections
    st.session_state.video_sequence = get_video_sequence(st.session_state.selected_videos)
    
    st.header("Wound Care Video Guide")
    
    #--------------------------------------------------
    # Display summary of selected options
    #--------------------------------------------------
    st.subheader("Selected Options:")
    
    options_text = ""
    for selection in st.session_state.selected_videos:
        for key, value in selection.items():
            if key != "video_ref":
                options_text += f"- **{key.replace('_', ' ').title()}**: {value.replace('_', ' ').title()}\n"
    
    st.markdown(options_text)
    
    #--------------------------------------------------
    # Display the video sequence
    #--------------------------------------------------
    st.subheader("Video Sequence:")
    
    # Loop through each video in the sequence
    for i, video_info in enumerate(st.session_state.video_sequence):
        ref = video_info.get("ref", "")
        title = video_info.get("title", "")
        
        # Create an expandable section for each video
        with st.expander(f"{i+1}. {title} (Ref: {ref})", expanded=True):
            # Check if this reference has a corresponding video file
            video_path = videos.get(ref, "")
            
            # Case 1: Local file exists
            if video_path and os.path.exists(video_path):
                st.video(video_path)
            
            # Case 2: S3 URL
            elif video_path and video_path.startswith("http"):
                try:
                    st.video(video_path)
                except Exception as e:
                    st.error(f"Error displaying video: {str(e)}")
                    st.info(f"You can access the video directly at: [{video_path}]({video_path})")
            
            # Case 3: Fallback to placeholder
            else:
                st.info(f"Video placeholder for {title} (Reference: {ref})")
                
                # Create visual placeholder
                st.markdown(
                    f"""
                    <div style="background-color: #e0e0e0; padding: 100px; border-radius: 5px; text-align: center;">
                        <h3>Video: {title}</h3>
                        <p>Reference: {ref}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    # Button to start a new guide
    if st.button("Start New Guide"):
        st.session_state.current_step = 'start'
        st.session_state.selected_videos = []
        st.session_state.video_sequence = []
        st.rerun()