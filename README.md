# Testwise- Online Examination Portal with Anti-Cheating

<center><img src="https://github.com/bhavyamistry/Testwise-OnlineExamPortal-with-AntiCheating/assets/58860047/40266a3e-8d5d-4eac-969b-d938aa48e030" width="40%" alt="vector" align="center"></center>

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


## Installation and Setup

To run the project locally, follow these steps:

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
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384.svg?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![jQuery](https://img.shields.io/badge/jquery-%230769AD.svg?style=for-the-badge&logo=jquery&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Microsoft Excel](https://img.shields.io/badge/Microsoft_Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)
![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)
![GoDaddy](https://img.shields.io/badge/GoDaddy-1BDBDB.svg?style=for-the-badge&logo=GoDaddy&logoColor=white)

## Live Demonstration

[![Demo](https://github.com/bhavyamistry/Testwise-OnlineExamPortal-with-AntiCheating/assets/58860047/683796cb-d14a-4795-a31a-71950d0d6ca0)](https://examportal.kjsieit.in/)

## Video Demonstration

https://user-images.githubusercontent.com/58860047/167340083-74c2b911-1c71-4be9-9e0c-6b805421d6eb.mp4


