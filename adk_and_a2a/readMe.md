<!-- To use A2A me need one of the agent to be deployed on cloud run -->

Step 1: Download and install the ADK and code samples

    py -m pip install --upgrade google-adk a2a-sdk google-genai
    
<!-- ***********************************************  -->

Step 2: Add your GCP details to .env

    cat << EOF > illustration_agent/.env
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID
    GOOGLE_CLOUD_LOCATION=global
    MODEL=gemini_flash_model_id
    IMAGE_MODEL=gemini_flash_image_model_id
    EOF

<!-- ***********************************************  -->

Step 3: Run the following to copy the .env to another agent directory 

    cp illustration_agent/.env slide_content_agent/.env

<!-- ***********************************************  -->

Step 4: Run and choose the agent wanna try(Illustration agent)

    adk run

<!-- ***********************************************  -->

Step 5: Deploy the agent

    adk deploy cloud_run \
    --project YOUR_GCP_PROJECT_ID \
    --region GCP_LOCATION \
    --service_name illustration-agent \
    --a2a \
    illustration_agent

<!-- ***********************************************  -->

Step 6: Enable another ADK agent to call this agent remotely

----> run the following command to copy the Agent Card JSON file to your adk_and_a2a directory and change its name to indicate that it represents the illustration_agent.

    cp illustration_agent/agent.json illustration-agent-card.json

----> Run and test ;)
<!-- ***********************************************  -->


<!-- Note: Most of the things are already prefilled in this case and might have to set the env vars if I have to run this once again and redeploy the agent :| -->
