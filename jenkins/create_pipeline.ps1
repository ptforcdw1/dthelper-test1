# jenkins/create_pipeline.ps1
# Creates a Jenkins pipeline job for a given DTHelper task.
# Usage: .\create_pipeline.ps1 -TaskId TASK-20260510-001
#
# Reads all URLs from config/environment.json.
# If Jenkins has security enabled, set JENKINS_USER and JENKINS_TOKEN env vars.

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskId,

    [string]$Description = ""
)

# --- Load config ---
$configPath = Join-Path $PSScriptRoot "..\config\environment.json"
$config     = Get-Content (Resolve-Path $configPath) -Raw | ConvertFrom-Json

$jenkinsUrl = $config.jenkins.url
$repoUrl    = $config.github.repo_url
$branch     = $config.github.branch
$jobName    = "dthelper-$TaskId"
$scriptPath = "jenkins/pipelines/task_$TaskId/Jenkinsfile"
$desc       = if ($Description) { $Description } else { "DTHelper pipeline for $TaskId" }

# --- Auth (optional — leave blank if Jenkins has no security) ---
$jenkinsUser  = [System.Environment]::GetEnvironmentVariable($config.jenkins.user_env_var)
$jenkinsToken = [System.Environment]::GetEnvironmentVariable($config.jenkins.token_env_var)
$credential   = $null
if ($jenkinsUser -and $jenkinsToken) {
    $pair       = "${jenkinsUser}:${jenkinsToken}"
    $encoded    = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $credential = "Basic $encoded"
}

# --- Get CSRF crumb (Jenkins enables this by default) ---
$crumbField = $null
$crumbValue = $null
try {
    $crumbHeaders = @{}
    if ($credential) { $crumbHeaders["Authorization"] = $credential }
    $crumbResp  = Invoke-RestMethod -Uri "$jenkinsUrl/crumbIssuer/api/json" `
                                    -Method Get -Headers $crumbHeaders -ErrorAction Stop
    $crumbField = $crumbResp.crumbRequestField
    $crumbValue = $crumbResp.crumb
} catch {
    # CSRF not enabled — proceed without crumb
}

# --- Build XML job config ---
$xmlConfig = @"
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>$desc</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.BooleanParameterDefinition>
          <name>RUN_TESTS</name>
          <defaultValue>true</defaultValue>
          <description>Run test.py after execute.py</description>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>DRY_RUN</name>
          <defaultValue>false</defaultValue>
          <description>Pass --dry-run to execute.py (no changes made)</description>
        </hudson.model.BooleanParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>$repoUrl</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/$branch</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>$scriptPath</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
"@

# --- POST to Jenkins API ---
$headers = @{ "Content-Type" = "application/xml" }
if ($credential)  { $headers["Authorization"] = $credential }
if ($crumbField)  { $headers[$crumbField]     = $crumbValue  }

$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($xmlConfig)

try {
    Invoke-RestMethod -Uri "$jenkinsUrl/createItem?name=$jobName" `
                      -Method Post `
                      -Body $bodyBytes `
                      -Headers $headers `
                      -ErrorAction Stop | Out-Null

    [ordered]@{
        success     = $true
        job_name    = $jobName
        jenkins_url = "$jenkinsUrl/job/$jobName"
        message     = "Pipeline created successfully"
    } | ConvertTo-Json

} catch {
    $statusCode = $null
    if ($_.Exception.Response) { $statusCode = [int]$_.Exception.Response.StatusCode }

    if ($statusCode -eq 400) {
        Write-Warning "Job '$jobName' already exists in Jenkins."
        [ordered]@{
            success     = $false
            job_name    = $jobName
            jenkins_url = "$jenkinsUrl/job/$jobName"
            message     = "Job already exists - no changes made"
        } | ConvertTo-Json
    } else {
        [ordered]@{
            success     = $false
            job_name    = $jobName
            status_code = $statusCode
            error       = $_.Exception.Message
        } | ConvertTo-Json
        exit 1
    }
}
