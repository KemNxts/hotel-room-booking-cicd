# Extra trusted CA certificates (optional)

**Normally this folder is empty and you do not need it.**

Some networks and antivirus products (for example Avast/AVG "HTTPS scanning",
or a company proxy) inspect HTTPS traffic by re-signing it with their own root
certificate. Windows trusts that certificate, but Linux containers do not, so
`pip install` inside `docker build` fails with:

    SSL: CERTIFICATE_VERIFY_FAILED ... unable to get local issuer certificate

Fix (pick one):

1. Turn the HTTPS inspection off (Avast: Settings -> Protection -> Core Shields
   -> Web Shield -> untick "Enable HTTPS scanning"), **or**
2. Export that root certificate in PEM format as a `.crt` file and put it in
   this folder. The Dockerfiles (app, Jenkins, Ansible controller, Ansible lab)
   add every `certs/*.crt` to the image's trusted list before downloading
   anything.

`*.crt` files here are git-ignored: they are machine-specific. A root CA
certificate is public information, not a secret, but it should not be shared
through the repository.

Export on Windows (PowerShell), e.g. for Avast:

```powershell
$c = Get-ChildItem Cert:\LocalMachine\Root | Where-Object Subject -like '*Avast*' | Select-Object -First 1
"-----BEGIN CERTIFICATE-----`n" + [Convert]::ToBase64String($c.RawData, 'InsertLineBreaks') + "`n-----END CERTIFICATE-----" |
  Set-Content -Encoding ascii certs\avast-root.crt
```
