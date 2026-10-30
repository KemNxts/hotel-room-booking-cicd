# Task 12 - viva questions and answers

**Task 12 - Jenkins-Docker Continuous Deployment**

Source: section G of [task-12-jenkins-docker-continuous-deployment.md](../../task-12-jenkins-docker-continuous-deployment.md) - answers checked against the
repository and the evidence in this project.

1. **CI vs CD?** CI builds and tests every change; CD goes further and
   automatically releases/deploys every change that passed.
2. **Why tag with version and SHA?** The version names the release; the SHA
   identifies the exact code. `1.1.0-1c2103c` links a container to one commit and one build.
3. **Registry vs Docker Hub?** A registry is any server that stores images;
   Docker Hub is one hosted public registry. We use our own local registry.
4. **Did you publish to Docker Hub?** No - it is implemented (`registry-creds`
   + REGISTRY parameter) but not tested; the local registry was demonstrated.
5. **How do you ensure only tested code is deployed?** Images are built after
   all tests pass, from a committed checkout; deploy uses `--no-build` with the pushed image; the health check compares the commit.
6. **(Project-specific) What runs in prod now and how do you know?**
   `1.1.0-d07929b` - `docker ps` shows the image and `/health` returns `"commit":"d07929b"`.
7. **(Project-specific) Why `docker compose pull` before `up`?** To deploy
   exactly what is in the registry - the same thing any other server would get.
8. **Where are registry credentials kept?** In Jenkins credentials
   (`registry-creds`), passed with `--password-stdin`; not needed for the local registry.
9. **Why keep old images?** For rollback: deploying an older tag needs no rebuild (shown in Task 14).
10. **Local registry limitation?** Only this machine can pull from it; a
    separate server would need a hosted registry (Docker Hub) or network access to it.

## Extra questions that match this demonstration

1. **Was Docker Hub used?**
   No. Publishing to Docker Hub is implemented (REGISTRY=docker.io/<id> plus the Jenkins credential registry-creds) but was never run, because it needs a Docker Hub account and an access token. A local registry, registry:2 on port 5000, was used and tested. Nothing was published externally and no registry credential is stored in the repository.

2. **How do you know the container is running exactly the image Jenkins tested and pushed?**
   Three matching facts: the version-commit tag that the build computed, the image labels and /health that report the same version and commit, and the image ID of the running container, which equals the image ID of the tag in the registry. The pipeline's health stage also greps /health for the exact version and commit of this build.

3. **Was a fresh container created by this deployment?**
   Yes: the Jenkins log shows 'Container hotel-staging-app-1 Recreate/Recreated' because the rebuilt image had a new image ID. Compose only recreates a container when its image or settings changed; the database stays in the named volume.
