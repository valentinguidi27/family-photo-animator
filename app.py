import streamlit as st
import replicate
import os
import tempfile

# Page Configuration
st.set_page_config(page_title="Family Photo Animator", page_icon="✨")

# --- CSS for a friendly look ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        border-radius: 10px;
    }
    h1 {
        text-align: center;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# --- App Logic ---
def main():
    st.title("✨ Magic Family Animator ✨")
    st.write("Upload a photo and watch AI bring it to life!")

    # 1. API Key Handling (For security when sharing)
    # We check if it's in secrets (for cloud) or ask user (for local)
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        api_token = st.secrets.get("REPLICATE_API_TOKEN")
    
    if not api_token:
        st.warning("⚠️ API Token missing.")
        api_token = st.text_input("Enter Replicate API Token:", type="password")

    # 2. File Uploader
    uploaded_file = st.file_uploader("Choose a picture...", type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None and api_token:
        # Display the image
        st.image(uploaded_file, caption="Original Photo", use_column_width=True)

        # 3. The Magic Button
        if st.button("🪄 Animate This Photo!"):
            os.environ["REPLICATE_API_TOKEN"] = api_token
            
            with st.spinner("AI is studying the image context and generating video... (this takes about 60 seconds)"):
                try:
                    # Save uploaded file to a temporary path because Replicate needs a path or URL
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # Call the Stable Video Diffusion model
                    # This model automatically understands context (water flows, fire flickers, etc.)
                    output = replicate.run(
                        "stability-ai/stable-video-diffusion:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                        input={
                            "input_image": open(tmp_path, "rb"),
                            "video_length": "25_frames_with_svd_xt", # Creates a smoother 4 second clip
                            "frames_per_second": 6
                        }
                    )

                    # Display the result
                    st.success("✨ Animation Complete!")
                    st.video(output)
                    
                    # Cleanup temp file
                    os.unlink(tmp_path)

                except Exception as e:
                    st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()