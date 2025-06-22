# Ghost Share: Anonymous File Sharing Platform
## Overview
Ghost Share is an anonymous file-sharing platform designed to prioritize user privacy and security. The application enables users to upload and download files anonymously, with robust protection mechanisms to prevent unauthorized access. This platform leverages modern technologies such as FastAPI, MongoDB, and Docker to deliver a seamless and secure user experience.

## Features
* Anonymous File Sharing: Securely upload and download files without revealing your identity.
* User Authentication: JWT and cookie-based authentication ensure that only authorized users can access the platform, safeguarding user data.
* Secure Data Management: MongoDB is used to efficiently store and manage file metadata, ensuring quick access and secure storage.
* High-Performance API: FastAPI is utilized to create responsive and efficient API endpoints, enhancing the overall user experience.
* Containerized Deployment: Docker is used to containerize the application, simplifying deployment and ensuring scalability.
## Technologies Used
* Backend: Python (FastAPI)
* Database: MongoDB
* Containerization: Docker
* Frontend: HTML, CSS, JavaScript
* Authentication: JWT, Cookies
## Installation
### Prerequisites
* MongoDB running locally or accessible remotely.
### Steps
1. Clone the repository:
```bash
git clone https://github.com/tharunteja77/Ghost-Share
```
2. Navigate to the project directory:
```bash
cd ghost-share
```
3. Access the application: Open your web browser and go to http://localhost:8000.
4. Use this command in terminal to run GHOST SHARE: ( Only if you have imported all the required modules in requirement.txt )
  ```bash
   uvicorn main:app --reload
```
   
## Usage
* First, sign up for ' Ghost Share ' to create your credentials. Once registered, you can log in using those credentials.
* Upload Files: Go to the upload page, select your file, and upload it securely.
* Download Files: Enter the provided download link to retrieve your file anonymously.
* Authentication: Register and log in to access the platform’s features securely.


