# ProtectMasterBot  :octocat:
![Deploy ProtectMasterBot to Azure Function App](https://github.com/GitHubAPIChallenge/ProtectMasterBot/workflows/Deploy%20ProtectMasterBot%20to%20Azure%20Function%20App/badge.svg)

ProtectMasterBot is a GitHub App  that enable you to protect your default branch.
To prevent commits from being lost due to accidental force pushes, you should protect your branch.
However, it's very hard to apply protection rules every single time right after your organization member create repository. This bot automate the process to apply the rule and inform you about the protection rules applied to the repository.

It's very easy to use ProtectMasterBot. Please install the bot in your organization.
Please Access **[HERE](https://github.com/apps/protectmasterbot)** to get the bot!

![](./contents/Installation.png)
### How to use


### 
![](./contents/HowToUse.png)

---
### Architecture and process
#### Process to protect master/main branch.
1. When your organization member create a new repository in the organization, ProtectMasterBot streams the repository's "created" event.
2. Azure Functions trigger ProtectMasterBot API. (```POST: /api/ProtectMaster```)
3. ProtectMasterBot API initiates the repository with README.md. The default branch is also created at the same time. 
4. ProtectMasterBot API protects default branch. ProtectMasterBot supports both master and main as default branch.
5. ProtectMasterBot API creats an issue in the repository. It also mentions specific user.
![](./contents/ProtectDiagram.png)

#### Process to register application
1. When the bot is installed, registration callback api on Azure Functions is called. (```GET: /api/ReceiveInstallation```)
2. The api registers organization and installation ID. After registration, the api provide a password to manage the servie setting.
3. User can edit ProtectMasterBot setting by accessing the edit page.(```GET: /api/EditRule```)
4. The API updates the CosmosDB.(```POST: /api/UpdateRule```)

![](./contents/ManagementDiagram.png)

### Host ProtectMasterBot by yourself

If you want to deploy ProtectMasterBot, you will need Azure environment.
ProtectMasterBot will be hosted on Azure Functions and also connect to Azure CosmosDB.
Deployment can be done by GitHub Actions.

#### Prerequisite
- Your GitHub Apps
- Azure Functions
- Azure CosmosDB


#### How to deploy API on Azure.

##### GitHub Apps setting

You will need PEM file and app ID for GitHub Apps beforehand.
Please refer below documents to get PEM file and App ID 
https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/

To learn more about GitHub Apps, please check below.
https://docs.github.com/ja/github-ae@latest/developers/apps/about-apps
##### On Azure Portal
1. Create Azure Functions
Please refer the below link for Azure Functions creation.
https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-azure-function
Note: You need to fill in the form with below specific parameters while creation.

Input |Parameters
---|-----
Publish | **code**
Runtime stack| **Python**
Version | **3.8**

2. Create CosmosDB
Please refer the below link for Azure CosmosDB deployment.
https://docs.microsoft.com/en-us/azure/cosmos-db/how-to-manage-database-account
Note: You need to fill in the form with below specific parameters while creation.

Input |Parameters
---|-----
API | Core (SQL)


3. Configure the Azure Functions
Please refer the below link for Azure Functions configuration
https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings
You need to add the environment variables below

Key|Value
---|-----
gh_app_pem | your GitHub App's PEM string which must be encoded with Base64
gh_app_id | GitHub Apps ID
cosmosdb_connection_string | Your CosmosDB connection string 

4. Get the Publishing Profile
Please refer the below link to get publishing profile (*.pubxml) 
https://docs.microsoft.com/en-us/visualstudio/deployment/tutorial-import-publish-settings-azure?view=vs-2019
You will use it for deployment

##### On GitHub
1. Set Secret for CI/CD
Please refer the below link to set the secret for CI/CD
https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets
You need to add the below secret

Secret Name|Value
---|-----
AZURE_FUNCTIONAPP_PUBLISH_PROFILE| Your downloaded publishing profile.

#### Setup GitHub Apps setting.
Finally, it's time to setup the GitHub Apps with the parameters
Please fill in the form with below parameter.

1. General Setting

Input|Value
---|---
Webhook URL| https://<YOUR_AZURE_FUNCTIONS_NAME>.azurewebsites.net/api/ProtectMaster

2. Permissions

Permissions|Value|Detail
---|---|---
Administration | Read & Write | This permission is necessary to apply branch protection rule
Contents | Read & Write | This permission is necessary to initiate repository with README.md
Issues | Read & Write | This permission is necessary to create an issue

3. Events

Subscribe to events|Check
---|---
Repository| true


NOW You are ready to use the bot!

---
#### How to run API in your local environment
You need to rename ```local.settings.json.sample``` as ```local.settings.json```, then set the values.
If you don't have PEM file and GitHub Apps id, you need to create GitHub Apps first. Please refer the documentation.
https://docs.github.com/ja/github-ae@latest/developers/apps/about-apps
Also, you need CosmosDB environment beforehand. You can deploy it on Azure and you can also use the CosmosDB emulator for local development if you want.
https://docs.microsoft.com/en-us/azure/cosmos-db/local-emulator?tabs=cli%2Cssl-netstd21

##### local.setting.json
```
"gh_app_pem": "<your pem string>",
"gh_app_id": "<your custom app id>",
"cosmosdb_connection_string": "<your CcosmosDBs connection string>"
```

##### Run Function
```sh
pip install -r requirements.txt
func start
```