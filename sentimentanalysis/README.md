# Arabic Sentiment Analysis with Streamlit and Firebase

This project is a web application built with Streamlit that performs sentiment analysis on Arabic text. The results are then stored and visualized in a dashboard powered by Firebase.

## Features

*   **Sentiment Analysis:** Analyzes Arabic text and classifies it as positive, negative, or neutral.
*   **Firebase Integration:** Stores the analysis results in a Firestore database.
*   **Interactive Dashboard:** Visualizes the sentiment data with charts and graphs.
*   **Data Export:** Allows users to download the data in CSV format.

## Technologies Used

*   **Python**
*   **Streamlit:** For the web application interface.
*   **Transformers:** For the sentiment analysis model (specifically, `PRAli22/AraBert-Arabic-Sentiment-Analysis`).
*   **Firebase (Firestore):** As the database to store the results.
*   **Pandas:** for data manipulation.
*   **Altair:** for data visualization.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Firebase credentials:**
    *   Create a file named `firebase-private-key.json` in the root of the project and place your Firebase private key in it. You can get this from your Firebase project settings.
    *   Create a file named `.env` in the root of the project.
    *   Add the following line to the `.env` file:
        ```
        firebase-private-key="firebase-private-key.json"
        ```

5.  **Run the application:**
    ```bash
    streamlit run sentimentapp.py
    ```

    You can then view the application in your browser at `http://localhost:8501`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
