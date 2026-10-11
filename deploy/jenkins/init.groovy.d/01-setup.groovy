// Runs each time Jenkins starts. Makes a fresh local Jenkins ready to use:
//   1. admin user (password from JENKINS_ADMIN_PASSWORD)
//   2. "hotel-secret-key" Secret-text credential (from HOTEL_SECRET_KEY)
//   3. "hotel-booking" pipeline job that reads the Jenkinsfile from the repo
// Everything here can also be done by hand in the Jenkins UI.
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import com.cloudbees.plugins.credentials.domains.Domain
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.GitSCM
import hudson.model.ChoiceParameterDefinition
import hudson.model.ParametersDefinitionProperty
import hudson.model.StringParameterDefinition
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import hudson.util.Secret
import jenkins.model.Jenkins
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def jenkins = Jenkins.get()
def env = System.getenv()

// 1. Security: one admin account, nothing visible without logging in.
//    Only on first start, so a password changed in the UI is not overwritten.
if (!(jenkins.securityRealm instanceof HudsonPrivateSecurityRealm)) {
    def realm = new HudsonPrivateSecurityRealm(false)  // false = no self sign-up
    realm.createAccount('admin', env['JENKINS_ADMIN_PASSWORD'])
    jenkins.securityRealm = realm
    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    strategy.allowAnonymousRead = false
    jenkins.authorizationStrategy = strategy
}

// 2. The app's SECRET_KEY, stored encrypted by Jenkins and injected into the
//    Deploy stage with withCredentials (never written in the Jenkinsfile).
if (env['HOTEL_SECRET_KEY']) {
    def store = SystemCredentialsProvider.instance.store
    def domain = Domain.global()
    def cred = new StringCredentialsImpl(CredentialsScope.GLOBAL, 'hotel-secret-key',
            'SECRET_KEY for the hotel booking app', Secret.fromString(env['HOTEL_SECRET_KEY']))
    def existing = store.getCredentials(domain).find { it.id == 'hotel-secret-key' }
    existing ? store.updateCredentials(domain, existing, cred) : store.addCredentials(domain, cred)
}

// 3. Pipeline job: "Pipeline script from SCM" pointing at our repository.
//    The branch is a build parameter (BRANCH), so the same job can build
//    develop, main or a throw-away experiment branch. The Jenkinsfile
//    declares the same parameters, so they survive its first run.
if (jenkins.getItem('hotel-booking') == null) {
    def repoUrl = env['HOTEL_REPO_URL'] ?: 'file:///repo'
    def branch = env['HOTEL_REPO_BRANCH'] ?: 'develop'
    def scm = new GitSCM(GitSCM.createRepoList(repoUrl, null),
            [new BranchSpec('*/${BRANCH}')], null, null, [])   // single quotes: Jenkins expands it per build
    def job = jenkins.createProject(WorkflowJob, 'hotel-booking')
    job.addProperty(new ParametersDefinitionProperty([
            new ChoiceParameterDefinition('APP_ENV', ['staging', 'prod'] as String[], 'Where to deploy'),
            new StringParameterDefinition('BRANCH', branch, 'Git branch to build'),
            new StringParameterDefinition('REGISTRY', 'localhost:5000', 'Image registry'),
    ]))
    def definition = new CpsScmFlowDefinition(scm, 'Jenkinsfile')
    definition.lightweight = false   // needed for a parameterised branch
    job.definition = definition
    job.save()
}

jenkins.save()
