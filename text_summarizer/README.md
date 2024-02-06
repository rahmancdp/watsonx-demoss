# Text Summarization Demo

This is a demo application showcasing text summarization capabilities. The backend server is built using Python FastAPI, and it consumes the Watsonx.ai API. The frontend is developed with Vue.js and utilizes the Carbon Design System as the theme. The main objective of this demo is to demonstrate the integration of Watsonx.ai through asynchronous API calls and to enhance the overall user experience.

## Technologies Used

- Backend:
  - Python FastAPI: A high-performance web framework for building APIs with Python.
  - Watsonx.ai: The AI and data platform by IBM, providing generative AI and machine learning capabilities.
- Frontend:
  - Vue.js: A progressive JavaScript framework for building user interfaces.
  - Carbon Design System: A set of pre-designed UI components based on IBM's design language.

## Functionality

The demo application allows users to input text and generate concise summaries based on the provided content. Here's an overview of the process:

1. User Interaction:
   - Users interact with the frontend interface developed with Vue.js and the Carbon Design System.
   - They input the text they want to summarize using the provided input field.

2. Asynchronous API Call:
   - The frontend makes an asynchronous API call to the backend server built with Python FastAPI.
   - The request is sent to the Watsonx.ai API, which performs the text summarization process.

3. Text Summarization:
   - Watsonx.ai's generative AI capabilities process the input text and generate a summary.
   - The summary is returned as a response to the API call.

4. Displaying the Summary:
   - The backend server receives the summary from Watsonx.ai.
   - The summary is sent back to the frontend as a response to the API call.
   - The frontend displays the generated summary to the user.

## Goals

The main goals of this demo are as follows:

- Showcase the integration of Watsonx.ai into a text summarization application.
- Demonstrate the usage of Python FastAPI as the backend server framework.
- Utilize Vue.js with the Carbon Design System to create an intuitive and visually appealing frontend.
- Implement asynchronous API calls to enhance the user experience by providing real-time feedback.

By combining these technologies and functionalities, we aim to provide users with an efficient and user-friendly text summarization experience.

**Note:** This is a demo application and may not reflect the full capabilities of Watsonx.ai or the final implementation of the project.