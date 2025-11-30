import streamlit as st
import replicate
import os
import tempfile
import requests

# Page Configuration
st.set_page_config(page_title="Joyeux Noël Lele", page_icon="🎄")

# --- CSS for a festive look ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #D42426; /* Christmas Red */
        color: white;
        height: 3em;
        border-radius: 10px;
        font-weight: bold;
    }
    h1 {
        text-align: center;
        color: #1E4620; /* Christmas Green */
    }
</style>
""", unsafe_allow_html=True)

# --- App Logic ---
def main():
    st.title("🎄 Joyeux Noël Lele 🎄")
    st.write("Téléchargez une photo et regardez la magie de Noël l'animer !")

    # 1. API Key Handling
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        api_token = st.secrets.get("REPLICATE_API_TOKEN")
    
    if not api_token:
        st.warning("⚠️ Clé API manquante.")
        api_token = st.text_input("Entrez votre clé API Replicate :", type="password")

    # 2. File Uploader (French labels)
    uploaded_file = st.file_uploader("Choisissez une photo...", type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None and api_token:
        # Display the image
        st.image(uploaded_file, caption="Photo originale", use_column_width=True)

        # 3. The Magic Button
        if st.button("🪄 Animer la photo !"):
            os.environ["REPLICATE_API_TOKEN"] = api_token
            
            with st.spinner("L'IA analyse l'image et crée la vidéo... (environ 1 minute)"):
                try:
                    # Save uploaded file to temp path
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # Call the AI Model
                    output = replicate.run(
                        "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                        input={
                            "input_image": open(tmp_path, "rb"),
                            "video_length": "25_frames_with_svd_xt",
                            "frames_per_second": 6
                        }
                    )

                    # output is usually a URL string from Replicate
                    video_url = output

                    # Display the result
                    st.success("✨ Animation terminée !")
                    st.video(video_url)
                    
                    # 4. Download Button Logic
                    # We fetch the video data from the URL so we can offer a file download
                    response = requests.get(video_url)
                    st.download_button(
                        label="⬇️ Télécharger la vidéo",
                        data=response.content,
                        file_name="joyeux_noel_lele.mp4",
                        mime="video/mp4"
                    )
                    
                    # Cleanup
                    os.unlink(tmp_path)

                except Exception as e:
                    st.error(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()
