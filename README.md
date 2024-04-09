# Testwise- Online Examination Portal with Anti-Cheating

![exam](https://github.com/bhavyamistry/Testwise-OnlineExamPortal-with-AntiCheating/assets/58860047/a1f749f4-7fec-4175-bb62-2eb7b460411d)

## Problem Statement

Traditional exam processes require physical invigilators to monitor candidates at exam centers, leading to logistical challenges and increased manual effort for assessing scanned answer copies. Moreover, the rise of online exams has exacerbated cheating practices, posing a threat to the integrity of assessments, especially amidst the challenges brought on by the COVID-19 pandemic.

## Project Overview

The Online Exam Proctoring System aims to address these challenges by providing a scalable solution for authenticating and monitoring online examinations. By leveraging remote proctoring capabilities, the system allows individual proctors to invigilate exams remotely, reducing the need for physical presence. Additionally, automated checking of candidate responses helps streamline the assessment process and ensures immediate feedback to students, thereby reducing anxiety and workload for educators.

## Features

- **Remote Exam Conduct**: Allow both students and invigilators to appear for and conduct exams remotely.
- **Authentication**: Secure authentication (JSON web token & Google SSO authorization) using a student university email account or with a Google organization account.
- **Password Reset System**: User-friendly system for resetting passwords securely.
- **Test Creation**: Easily create tests with customizable parameters and question formats.
- **Upload from Excel**: Seamlessly upload exam questions from Excel files for efficient data management.
- **Master Data Management**: Manage student, faculty, and subject data with options to add, update, or delete records.
- **Optimization for Large Responses**: Handle large volumes of responses from students efficiently.
- **Scalable Online Portal**: Authenticate, authorize, and control online examination processes in a scalable manner.
- **Automated Answer Assessment**: Reduce manual assessment workload with automated assessment of scanned answer copies.
- **Cheating Detection Measures**: Implement measures to detect and prevent cheating during examinations.
- **Tab Switching Prevention**: Prevent students from switching tabs during exams to maintain exam integrity.
- **Full-Screen Mode**: Enable full-screen mode for a distraction-free exam experience.
- **Rapid Score Release**: Speed up assessment and release scores quickly to maintain efficiency.
- **Results Visualization**: Visualize exam results with intuitive charts and graphs, exportable to Excel sheets.

## Installation

## Installation

To run the project locally, follow these steps:

### Installation and Setup

1. **Create an .env file**: Create a file named `.env` in the project directory.

2. **Add the following lines to the .env file**:

    ```
    FLASK_APP=app.py
    FLASK_DEBUG=1
    FLASK_RUN_PORT=3000
    APP_SECRET_KEY=IOAJODJAD89ADYU9A78YGD
    ```

3. **Create a Python environment**: Open your terminal and run the following command to create a Python virtual environment named `quiz-env`:

    ```
    python -m venv quiz-env
    ```

4. **Activate the environment**: Activate the virtual environment by running the following command:

    ```
    quiz-env\Scripts\activate.bat
    ```

5. **Install dependencies**: Run the following command to install the required dependencies from the `requirements.txt` file:

    ```
    pip install -r requirements.txt
    ```

6. **Run the server**: Finally, start the Flask server by running the following command:

    ```
    flask run
    ```

Now, you should be able to access the project locally at [http://localhost:3000/](http://localhost:3000/).

## Technologies-used
![C#](https://img.shields.io/badge/c%23-%23239120.svg?style=for-the-badge&logo=csharp&logoColor=white)
![.Net](https://img.shields.io/badge/.NET-5C2D91?style=for-the-badge&logo=.net&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![MicrosoftSQLServer](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft%20sql%20server&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Google Web Speech API](https://img.shields.io/badge/google%20assistant-4285F4?style=for-the-badge&logo=google%20web%20speech%20API&logoColor=white)

## Live Demonstration

Check out the live demo of the project [here](https://examportal.kjsieit.in/) [![Demo](https://github.com/bhavyamistry/Akamai-Smart-Desktop-Assistant-for-Windows/blob/main/assets/58860047/c34348ff-17b8-4008-8e06-8436bcf0ac27.png)](https://examportal.kjsieit.in/)

## Video Demonstration

https://user-images.githubusercontent.com/58860047/167340083-74c2b911-1c71-4be9-9e0c-6b805421d6eb.mp4


