# Fabula

You work for a software engineering company and develop custom software for clients. One of the clients requested a proof of concept (PoC) for a web application that allows users to upload pictures and receive weather-related results (e.g., rainy, foggy, sunny). The client received a demo of this project, but it was postponed due to budget constraints. Additionally, the original developer of the PoC left the company, and no one is familiar with how it functions.

The client now wishes to continue the project as soon as possible, and you are assigned to lead it. Currently, you are the only person responsible for CI/CD and systems architecture on the project.

## Technical considerations
 
- The client aims to create a cloud-native solution. Although they haven’t decided on a specific cloud provider, they expect all required environments, CI/CD pipelines, and databases to be hosted with one of the top cloud vendors.
- The client has several SCM tools in place: GitHub, GitLab, Bitbucket, Azure DevOps, and Forgejo (self-hosted). You can use any of these to demonstrate the benefits of integrated CI/CD, with the flexibility to migrate to the client's preferred SCM in the future.

## Expectations

- You will need to create a systems design with supporting diagrams and documentation.
- There is a scheduled meeting with the client’s team, which includes project managers, architects, and a technical lead.
  * They expect to see a production-grade SDLC with a fully implemented CI/CD pipeline.
  * They are looking forward to a quick product demo, so the application should be deployed to a production-like environment.
  * The client has recently started adopting IaC and hopes to run a pilot using best practices during this project.
  * Expect technical questions and discussions regarding the solution details and technical implementation.
  * Be prepared for live coding, as they may request you to implement a new feature on the spot.
- The client’s architect has conducted an independent analysis and proposed a high-level solution. This includes a container orchestration system, IaC, fully automated SDLC (including SAST and DAST), and an enterprise-grade database.
- Our consulting team is available to assist if needed (a Teams chat will be created soon after you receive this assignment).

## Hints and Tips from consultancy team:
- Free accounts on public SCM platforms and free-tier cloud providers are sufficient for this assignment.
- You have approximately 7 days to complete this task.
- "Talk is cheap. Show me the code." © Linus Torvalds. By day 5, you should provide access to the repository(ies) and, if available, to the deployed application for review by the assessment committee.
- The task can be completed in approximately 20 hours, so plan your time accordingly.
- Certain parts can be stubbed or skipped to save time. For example, you may skip unit test implementation in your CI pipeline and instead create a placeholder step that always returns success.
- Code can be broken. Verify that the application works as expected (if it possible), and address any issues that arise.
- Use GenAI or other AI tools to streamline your work, but don’t overlook your own expertise.
- You always have space to improvements. If you identify any minor additions that could significantly improve the quality of the solution, feel free to implement it.


----
# Project description
![Image](docs/conceptual.png)

# Project Structure

## Categorize
VGG-19 network and application code to perform inference

## Common
Storage, config and queue code

## Dispatcher
Backend to get pictures and handle user response

## Docs
Documentation-related images and files

## Reporting
Collection and visualization of user activity

## UI
User interface files

# Concepts
This project was intentionally created the way it was created
