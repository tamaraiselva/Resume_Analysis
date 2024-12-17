import streamlit as st
import pdfplumber
from sentence_transformers import SentenceTransformer, util

# Text Extraction from PDF
def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return text
    except Exception as e:
        return ""

# BERT Similarity Calculation
def calculate_bert_similarity(job_description, resumes):
    # Load the BERT model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Encode the job description and resumes
    embeddings = model.encode([job_description] + resumes, convert_to_tensor=True)

    # Calculate cosine similarity (outputs a tensor)
    similarities_tensor = util.pytorch_cos_sim(embeddings[0], embeddings[1:])
    
    # Convert tensor to a list of similarity scores
    similarities = similarities_tensor.squeeze().tolist()

    # Ensure similarities is a list even if there's only one resume
    if isinstance(similarities, float):  # If only one resume, pytorch_cos_sim returns a float
        similarities = [similarities]

    return similarities

# Convert Similarity Scores to Percentage
def convert_to_percentage(similarity_scores):
    return [score * 100 for score in similarity_scores]

# Main App Function
def main():
    st.title("Resume Analysis and Candidate Evaluation")
    st.write("Upload multiple resumes (PDFs) and provide a job description to rank candidates by their relevance.")

    # Upload Resume Files
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", accept_multiple_files=True, type=["pdf"])

    # Paste Job Description
    job_description = st.text_area("Paste Job Description", height=150)

    # Process and Rank Resumes
    if st.button("Rank Resumes"):
        if not uploaded_files or not job_description.strip():
            st.error("Please upload resumes and provide a job description.")
            return

        # Extract text from resumes
        resume_texts = []
        resume_names = []
        for file in uploaded_files:
            text = extract_text_from_pdf(file)
            if text.strip():
                resume_texts.append(text)
                resume_names.append(file.name)
            else:
                st.error(f"Could not extract text from {file.name}. It might be a scanned document.")

        if not resume_texts:
            st.error("No valid resumes found. Please upload readable files.")
            return

        # Calculate Similarity Scores using BERT
        scores = calculate_bert_similarity(job_description, resume_texts)

        # Convert scores to percentages
        percentages = convert_to_percentage(scores)

        # Rank Resumes
        ranked_resumes = sorted(zip(resume_names, percentages), key=lambda x: x[1], reverse=True)

        # Display Results in the desired format
        st.subheader("Ranked Resumes (Matching Percentages)")
        for rank, (name, percentage) in enumerate(ranked_resumes, start=1):
            st.write(f"{rank}. {name} -  {percentage:.2f}%")

        # Success message after ranking resumes
        st.success("Resumes have been successfully ranked!")

if __name__ == "__main__":
    main()
