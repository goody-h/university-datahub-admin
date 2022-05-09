# University DataHub

A result collation and analytics software for Higher Institutions.

## Introduction

Manual computation of results has been a nightmare fraught with issues and challenges. Preparing handwritten score sheets for courses meant that individual results for students had to be transferred manually to the student&#39;s result spreadsheet. A process that is error-prone and also time-consuming. Preparing the score sheets with a spreadsheet program such as Microsoft Excel is an improvement. However, if left in this state, it produces no noticeable gains. Still, it requires the manual collation process that plagues the handwritten state, negating all the possible benefits of having the data in digital form.

The application of some data transformation processes can accurately convert the data to a format that allows for rapid manipulation, transfer, and analysis.

## Scope/Features

The software has been designed to achieve the following:

1. Convert and securely store Excel-based data in an intermediate format such as a relational database schema. The following features achieve this.

    - A password/cryptographically protected upload feature accepts three categories of Excel data.

        - Courses and configuration (no. of semesters, max sessions, HOD, etc.) for the department or program.
        - Biodata of students in the department (Name, graduation status, deferments, waivers, etc.).
        - Score sheets for courses offered in the department.

    - It allows the configuration of multiple data storage profiles.
    - It allows the configuration of several departments/programs per profile.
    - It provides data restore and backup functionality.
    - It provides a remote data storage and synchronization (online or on-premises) option, allowing for multiple remote connections.
    - It provides a Read-only configuration mode, preventing uploading/modifications of data for additional security.

2. Generate Result Spreadsheet (in Excel format) for individual students while performing comprehensive analytics and anomaly detection such as:

    - It includes the student&#39;s biodata on the spreadsheet.
    - It computes the CGPA and GPA per semester.
    - It detects invalid courses not offered by the department.
    - It detects carryover results and ensures a maximum grade of &#39;C.&#39;
    - It detects a retake for an already passed course.
    - It detects maliciously uploaded results.
    - It ensures that the elective requirements per semester are fulfilled.
    - It detects exceeded credit loads per semester.
    - It detects results with invalid sessions.
    - It detects additional results in prohibited semesters, such as a SIWES semester.
    - It detects possible deferred sessions.
    - It detects invalid results in specified deferred sessions.
    - It detects specified waivers.
    - It specifies outstanding courses (Courses not taken or passed yet) up to the current semester.

3. Generate a Standard Graduation Degree Result (in Excel format). The degree result is generated for specified students and follows the standard pattern currently in use.

4. Generate a concise Result Analytics Dashboard/Solution (in Excel format). The solution provides comprehensive insights into the performance and state of results for specified students. It offers the following functionalities:

    - It specifies the overall performance of students per semester, including current CGPA and Class.
    - It provides Direct access/link to individual spreadsheets from the analytics page.
    - It specifies the number of outstanding carryovers for each student.
    - It indicates any underlying issues, if any, with any student&#39;s result spreadsheet.
    - It provides adequate color-coding to detect issues and states of each record efficiently.
    - It specifies the graduation state of each student.
    - It specifies any outstanding courses or waivers in each student&#39;s spreadsheet.
    - It allows the sorting of records based on specified criteria such as name, CGPA, graduation status, etc.


## Technology
Programming language: python

UI library: PyQt5

Data Input: Microsoft Excel

Data Output: Microsoft Excel + Excel VBA

Data storage:
- Remote: Microsoft SQL Server, Postgres, MySQL – Azure/AWS
- Local: SQLite

Security: RSA Cryptography, SHA256

Packaging: PyInstaller – Windows
