Feature: Return details of GitHub repositories with the topic "kubernetes"
  Queries GitHub's API and returns 500 repos with the topic "kubernetes"

  Scenario: Return unsorted kubernetes related repositories
      Given the API server is running
       When the user accesses the /api/kubernetes endpoint
       Then 500 repositories are returned
