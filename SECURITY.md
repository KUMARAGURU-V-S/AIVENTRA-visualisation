# Security & Compliance

This project implements industry-standard security practices to ensure the integrity and safety of the codebase and its dependencies.

## Security Tooling

We utilize the following tools for continuous security monitoring:

- **[Syft](https://github.com/anchore/syft)**: A powerful tool for generating a Software Bill of Materials (SBOM) from container images and filesystems.
- **[Grype](https://github.com/anchore/grype)**: A vulnerability scanner for container images and filesystems, designed to work seamlessly with Syft.

## Software Bill of Materials (SBOM)

An SBOM is a comprehensive inventory of all software components, dependencies, and metadata in a project. We generate our SBOM in **CycloneDX** format (see `project-sbom.json`).

### Why this is good:
- **Transparency**: Provides a clear view of all direct and indirect dependencies.
- **Vulnerability Management**: Allows for rapid identification of components affected by new CVEs (Common Vulnerabilities and Exposures).
- **Compliance**: Meets emerging regulatory requirements for software supply chain security.
- **License Management**: Helps track and manage open-source licenses within the project.

## Vulnerability Scanning

We use Grype to scan our SBOM and source code for known vulnerabilities.

### Why this is good:
- **Proactive Security**: Identifies security flaws in dependencies before they can be exploited.
- **Severity-based Prioritization**: Categorizes vulnerabilities by severity (Critical, High, Medium, Low), allowing us to focus on the most urgent fixes first.
- **Continuous Monitoring**: Can be integrated into CI/CD pipelines to prevent insecure code from being deployed.

## Current Status

As of the latest scan:
- **SBOM**: Generated and up-to-date in `project-sbom.json`.
- **Vulnerabilities**: Monitored and tracked for remediation.

---
*Note: This security documentation was automatically updated to reflect the integration of Syft and Grype.*
