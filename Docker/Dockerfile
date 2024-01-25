# syntax=docker/dockerfile:1
# escape=`

ARG BASE_IMAGE=mcr.microsoft.com/windows:ltsc2019
ARG DPF_PACKAGE_VERSION=24.2.pre0
ARG DPF_PACKAGE_VERSION_NO_DOTS=2024_2_pre0

##########################################
#     BASE WITH VISUAL STUDIO TOOLS      #
##########################################
FROM $BASE_IMAGE AS libraries_installer

ARG BASE_IMAGE

# Set LABEL org.opencontainers.image.created with the command line, use:
# Powershell : Get-Date -Format o | ForEach-Object { $_ -replace ":", "." }
# bash: $(date --utc +%FT%TZ)
LABEL org.opencontainers.image.title="ANSYS DPF Sound"
LABEL org.opencontainers.image.description="Windows container image with ANSYS DPF and ANSYS DPF Sound plugin."
LABEL org.opencontainers.image.base.name=$BASE_IMAGE

# Set the default Windows shell for correct batch processing.
SHELL ["cmd", "/S", "/C"]

WORKDIR C:\\

RUN `
    # Download the Build Tools bootstrapper.
    curl -SL --output vs_redist.exe https://aka.ms/vs/17/release/vc_redist.x64.exe `
    `
    # Install Build Tools with the Microsoft.VisualStudio.Workload.AzureBuildTools workload, excluding workloads and components with known issues.
    && (start /w vs_redist.exe /quiet /norestart /install) `
    `
    # Cleanup
    && del /q vs_redist.exe


##########################################
#               DPF SERVER               #
##########################################
FROM libraries_installer

ARG DPF_PACKAGE_VERSION
ARG DPF_PACKAGE_VERSION_NO_DOTS

LABEL com.ansys/dpf.version=$DPF_PACKAGE_VERSION

EXPOSE 50052

SHELL ["cmd", "/S", "/C"]

#RUN setx /m PATH "%PATH%;C:\\ansys\\sound"
RUN setx /m PATH "%PATH%;C:\\ansys\\dpf\\server_${DPF_PACKAGE_VERSION_NO_DOTS}\\Acoustics\\SAS"

COPY ansys C:\\ansys
# COPY ansys ansys_inc

# Probably need to change the path below
# WORKDIR C:\\ansys_inc\\ansys\\dpf\\server_${DPF_PACKAGE_VERSION_NO_DOTS}\\aisol\\bin\\winx64\\
WORKDIR C:\\ansys\\dpf\\server_${DPF_PACKAGE_VERSION_NO_DOTS}\\aisol\\bin\\winx64\\

# Define the entry point for the docker container.
# This entry point starts the developer command prompt and launches the PowerShell shell.
ENTRYPOINT ["cmd", "/S", "/C", ".\\Ans.Dpf.Grpc.bat"]
