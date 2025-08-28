# cleanup_old_system.ps1 - PowerShell script to clean up the old over-engineered system

# Set error action preference
$ErrorActionPreference = "Continue"

function Show-Header {
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "OLD SYSTEM CLEANUP UTILITY" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This script will help you clean up resources from the old over-engineered system." -ForegroundColor Yellow
    Write-Host "It will stop and remove Docker containers, networks, and volumes." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WARNING: This will remove all Docker containers, networks, and volumes related to the old system." -ForegroundColor Red
    Write-Host "Make sure you have backed up any important data before proceeding." -ForegroundColor Red
    Write-Host ""
}

function Check-Docker {
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker detected: $dockerVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker not found or not running!" -ForegroundColor Red
        Write-Host "Please make sure Docker Desktop is installed and running." -ForegroundColor Red
        return $false
    }
}

function Stop-DockerContainers {
    Write-Host "Stopping Docker containers..." -ForegroundColor Cyan
    
    # Get list of running containers
    $containers = docker ps -a --format "{{.Names}}" 2>$null
    
    if ($containers) {
        foreach ($container in $containers) {
            Write-Host "Stopping container: $container" -ForegroundColor Yellow
            docker stop $container 2>$null
        }
        Write-Host "✅ All containers stopped" -ForegroundColor Green
    }
    else {
        Write-Host "No running containers found" -ForegroundColor Yellow
    }
}

function Remove-DockerContainers {
    Write-Host "Removing Docker containers..." -ForegroundColor Cyan
    
    # Get list of all containers
    $containers = docker ps -a --format "{{.Names}}" 2>$null
    
    if ($containers) {
        foreach ($container in $containers) {
            Write-Host "Removing container: $container" -ForegroundColor Yellow
            docker rm -f $container 2>$null
        }
        Write-Host "✅ All containers removed" -ForegroundColor Green
    }
    else {
        Write-Host "No containers found" -ForegroundColor Yellow
    }
}

function Remove-DockerNetworks {
    Write-Host "Removing Docker networks..." -ForegroundColor Cyan
    
    # Get list of custom networks (excluding default ones)
    $networks = docker network ls --filter "type=custom" --format "{{.Name}}" 2>$null
    
    if ($networks) {
        foreach ($network in $networks) {
            # Skip default networks
            if ($network -ne "bridge" -and $network -ne "host" -and $network -ne "none") {
                Write-Host "Removing network: $network" -ForegroundColor Yellow
                docker network rm $network 2>$null
            }
        }
        Write-Host "✅ All custom networks removed" -ForegroundColor Green
    }
    else {
        Write-Host "No custom networks found" -ForegroundColor Yellow
    }
}

function Remove-DockerVolumes {
    Write-Host "Removing Docker volumes..." -ForegroundColor Cyan
    
    # Ask for confirmation before removing volumes
    Write-Host "WARNING: This will remove all Docker volumes, which may contain important data." -ForegroundColor Red
    $confirm = Read-Host "Are you sure you want to proceed? (y/n)"
    
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Skipping volume removal" -ForegroundColor Yellow
        return
    }
    
    # Get list of volumes
    $volumes = docker volume ls --format "{{.Name}}" 2>$null
    
    if ($volumes) {
        foreach ($volume in $volumes) {
            Write-Host "Removing volume: $volume" -ForegroundColor Yellow
            docker volume rm $volume 2>$null
        }
        Write-Host "✅ All volumes removed" -ForegroundColor Green
    }
    else {
        Write-Host "No volumes found" -ForegroundColor Yellow
    }
}

function Remove-DockerImages {
    Write-Host "Removing Docker images..." -ForegroundColor Cyan
    
    # Ask for confirmation before removing images
    Write-Host "WARNING: This will remove all Docker images." -ForegroundColor Red
    $confirm = Read-Host "Are you sure you want to proceed? (y/n)"
    
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Skipping image removal" -ForegroundColor Yellow
        return
    }
    
    # Get list of images
    $images = docker images --format "{{.Repository}}:{{.Tag}}" 2>$null
    
    if ($images) {
        foreach ($image in $images) {
            # Skip <none>:<none> images
            if ($image -ne "<none>:<none>") {
                Write-Host "Removing image: $image" -ForegroundColor Yellow
                docker rmi -f $image 2>$null
            }
        }
        
        # Remove dangling images
        Write-Host "Removing dangling images..." -ForegroundColor Yellow
        docker image prune -f 2>$null
        
        Write-Host "✅ All images removed" -ForegroundColor Green
    }
    else {
        Write-Host "No images found" -ForegroundColor Yellow
    }
}

function Clean-DockerSystem {
    Write-Host "Cleaning up Docker system..." -ForegroundColor Cyan
    
    # Run docker system prune
    Write-Host "Running docker system prune..." -ForegroundColor Yellow
    docker system prune -f 2>$null
    
    Write-Host "✅ Docker system cleaned" -ForegroundColor Green
}

function Stop-DockerCompose {
    Write-Host "Stopping Docker Compose services..." -ForegroundColor Cyan
    
    # Check if docker-compose.yml exists
    if (Test-Path "docker-compose.yml") {
        Write-Host "Found docker-compose.yml, stopping services..." -ForegroundColor Yellow
        docker-compose down 2>$null
        Write-Host "✅ Docker Compose services stopped" -ForegroundColor Green
    }
    elseif (Test-Path "./automated-cashflow-pipeline/docker-compose.yml") {
        Write-Host "Found docker-compose.yml in automated-cashflow-pipeline, stopping services..." -ForegroundColor Yellow
        Set-Location ./automated-cashflow-pipeline
        docker-compose down 2>$null
        Set-Location ..
        Write-Host "✅ Docker Compose services stopped" -ForegroundColor Green
    }
    else {
        Write-Host "No docker-compose.yml found" -ForegroundColor Yellow
    }
    
    # Check for other docker-compose files
    $composeFiles = Get-ChildItem -Path . -Filter "docker-compose*.yml" -Recurse
    foreach ($file in $composeFiles) {
        Write-Host "Found $($file.FullName), stopping services..." -ForegroundColor Yellow
        Set-Location $file.Directory
        docker-compose -f $file.Name down 2>$null
        Set-Location $PSScriptRoot
    }
}

function Kill-DockerProcesses {
    Write-Host "Checking for stuck Docker processes..." -ForegroundColor Cyan
    
    # Get list of Docker processes
    $processes = Get-Process | Where-Object { $_.ProcessName -like "*docker*" -or $_.ProcessName -like "*compose*" } | Where-Object { $_.ProcessName -ne "dockerd" -and $_.ProcessName -ne "com.docker.service" }
    
    if ($processes) {
        Write-Host "Found the following Docker-related processes:" -ForegroundColor Yellow
        $processes | Format-Table -Property Id, ProcessName, StartTime -AutoSize
        
        $confirm = Read-Host "Do you want to kill these processes? (y/n)"
        
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            foreach ($process in $processes) {
                Write-Host "Killing process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
            Write-Host "✅ Processes killed" -ForegroundColor Green
        }
        else {
            Write-Host "Skipping process termination" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "No stuck Docker processes found" -ForegroundColor Yellow
    }
}

function Free-DockerPorts {
    Write-Host "Checking for processes using Docker ports..." -ForegroundColor Cyan
    
    # Common Docker ports
    $ports = @(2375, 2376, 8000, 8001, 8002, 8003, 8080, 9000, 9090, 3000, 5000, 5432, 6379)
    
    foreach ($port in $ports) {
        $processInfo = netstat -ano | findstr ":$port "
        if ($processInfo) {
            Write-Host "Found process using port $port:" -ForegroundColor Yellow
            Write-Host $processInfo -ForegroundColor Yellow
            
            # Extract PID
            $pid = ($processInfo -split ' ')[-1]
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                    
                    $confirm = Read-Host "Do you want to kill this process? (y/n)"
                    if ($confirm -eq "y" -or $confirm -eq "Y") {
                        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                        Write-Host "✅ Process killed" -ForegroundColor Green
                    }
                }
            }
            catch {
                Write-Host "Could not get process information for PID: $pid" -ForegroundColor Red
            }
        }
    }
}

function Main {
    Show-Header
    
    $confirm = Read-Host "Do you want to proceed with cleanup? (y/n)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Cleanup cancelled" -ForegroundColor Yellow
        return
    }
    
    # Check if Docker is running
    $dockerRunning = Check-Docker
    if (-not $dockerRunning) {
        $startDocker = Read-Host "Do you want to try to clean up without Docker? (y/n)"
        if ($startDocker -ne "y" -and $startDocker -ne "Y") {
            Write-Host "Cleanup cancelled" -ForegroundColor Yellow
            return
        }
    }
    else {
        # Stop Docker Compose services
        Stop-DockerCompose
        
        # Stop and remove containers
        Stop-DockerContainers
        Remove-DockerContainers
        
        # Remove networks
        Remove-DockerNetworks
        
        # Ask about removing volumes
        Remove-DockerVolumes
        
        # Ask about removing images
        Remove-DockerImages
        
        # Clean up Docker system
        Clean-DockerSystem
    }
    
    # Kill stuck Docker processes
    Kill-DockerProcesses
    
    # Free Docker ports
    Free-DockerPorts
    
    Write-Host ""
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "CLEANUP COMPLETE" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "The old system has been cleaned up." -ForegroundColor Green
    Write-Host "You can now use the new minimal trading system." -ForegroundColor Green
    Write-Host ""
    Write-Host "To set up the new system:" -ForegroundColor Yellow
    Write-Host "1. Run install_dependencies.bat to install required packages" -ForegroundColor Yellow
    Write-Host "2. Run python create_env_file.py to set up your API credentials" -ForegroundColor Yellow
    Write-Host "3. Run powershell -ExecutionPolicy Bypass -File start_trading_system.ps1 to start trading" -ForegroundColor Yellow
    Write-Host ""
}

# Run the main function
Main