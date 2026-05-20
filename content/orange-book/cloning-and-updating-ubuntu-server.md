---
title: "Cloning an Ubuntu Server Drive and Safely Updating Your Stack"
date: 2026-05-11
description: "A hands-on walkthrough of cloning an Ubuntu Server installation to a larger NVMe drive, expanding LVM to use the full disk, and safely updating OS packages and Docker containers without taking down your services."
tags:
  - homelab
  - ubuntu
  - linux
  - sysadmin
  - docker
categories:
  - Orange Book
author: "Logan"
draft: false
---

Running a homelab Ubuntu server long enough and you'll hit two milestones eventually: the drive fills up and you need to migrate to a larger one, and your stack needs a proper maintenance pass to stay current. Both operations are straightforward once you understand the order of operations — but get either one wrong and you're looking at an unbootable system or a fleet of containers that won't start.

This walkthrough covers both from start to finish, based on a real migration from a saturated SSD to a 476.9G NVMe on an Ubuntu Server 24.04 LTS host running Docker, LVM, and a Cloudflare Tunnel.

---

## Part 1: Cloning to a Larger Drive

### The Situation

The source drive was sitting at 90% capacity — 84G used out of 98G available. A new NVMe had been installed alongside it. The goal: clone everything, expand the filesystem to use the full drive, and come back up cleanly.

### Step 1: Pre-Shutdown — Stop Your Containers

Never clone a live system with running containers if you can avoid it. Filesystems in active use during a block-level clone can result in a corrupted target. Bring everything down cleanly first.

```bash
# List active compose stacks
docker compose ls

# Stop each stack
docker compose -f /path/to/docker-compose.yml down

# Stop any manually managed containers
docker stop <container_name>

# Confirm nothing is running
docker ps
```

Once `docker ps` returns empty, verify your partition layout and note your drive identifiers:

```bash
lsblk
blkid
```

Keep the `blkid` output handy — you may need it to verify UUIDs after the clone.

### Step 2: Boot from a Live USB and Clone with dd

Shut down the server and boot from a live Ubuntu USB. You need to be off the source drive before cloning it.

From the live environment, identify your source and target drives with `lsblk`, then run the clone:

```bash
sudo dd if=/dev/[source_drive] of=/dev/nvme0n1 bs=4M status=progress conv=fsync
```

- `bs=4M` — 4MB block size strikes a good balance between speed and reliability
- `status=progress` — shows live transfer rate and completion estimate
- `conv=fsync` — flushes writes to disk before exiting, preventing a silent partial clone

This will take a while depending on drive size. Let it finish completely before doing anything else.

### Step 3: Expand the LVM (The Step Everyone Forgets)

This is where most guides stop short. After the clone, if you boot up and run `df -h`, you'll likely see the same ~98G of usable space you had before — not the full 471G the new drive offers. That's because Ubuntu Server uses LVM by default and the logical volume was only sized for the original drive.

Three commands fix this, in sequence:

```bash
# 1. Tell LVM the physical volume now has more space
sudo pvresize /dev/nvme0n1p3

# 2. Extend the logical volume to consume all newly available space
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv

# 3. Resize the ext4 filesystem to fill the logical volume
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv
```

Verify it worked:

```bash
df -h /
```

You should now see the full capacity available. In this case, the filesystem went from 98G to ~471G.

> **Why three commands?** LVM separates physical storage (PV), logical grouping (VG), and usable volumes (LV). `pvresize` updates the PV boundary, `lvextend` grows the LV within the VG, and `resize2fs` tells the filesystem about the new LV size. Skipping any one of them leaves the other layers unaware of the extra space.

### Step 4: Bring Services Back Up

```bash
docker compose -f /path/to/docker-compose.yml up -d
docker start <manually_managed_containers>
docker ps
```

Verify everything is running and healthy before calling it done.

---

## Part 2: Safely Updating Ubuntu Server and Docker

Maintenance updates on a production homelab box require a specific order to avoid taking down services longer than necessary and to catch driver issues before they strand you.

### The Order That Matters

1. OS packages first
2. Pull new Docker images (while old containers are still running)
3. Redeploy stacks with updated images
4. Handle any driver issues post-reboot

### Step 1: OS Package Updates

```bash
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y && sudo apt autoclean
```

Read the upgrade output carefully. Pay attention to:

- **Kernel updates** — a new kernel requires a reboot before it takes effect
- **NVIDIA driver updates** — if `nvidia-*` packages appear in the upgrade list, plan for a reboot and potential driver/library mismatch before your GPU containers will start again
- **Service restarts** — `needrestart` may prompt you about services that need restarting

### Step 2: Pull Updated Docker Images

Pull images while your containers are still running. This minimizes downtime since the pull happens in the background:

```bash
docker compose -f /path/to/stack1/docker-compose.yml pull
docker compose -f /path/to/stack2/docker-compose.yml pull
docker compose -f /path/to/stack3/docker-compose.yml pull
```

Services tagged `Skipped - No image to be pulled` are locally built images. Those get rebuilt separately if needed — pulling won't update them.

### Step 3: Redeploy Stacks

```bash
docker compose -f /path/to/stack1/docker-compose.yml up -d --pull always
docker compose -f /path/to/stack2/docker-compose.yml up -d --pull always
docker compose -f /path/to/stack3/docker-compose.yml up -d --pull always
```

`--pull always` forces Docker to use the freshly pulled image even if the local tag appears current.

### Step 4: Update Manually Managed Containers

Containers not managed by Compose (like Portainer) need to be stopped, removed, re-pulled, and re-run:

```bash
docker stop portainer && docker rm portainer
docker pull portainer/portainer-ce
docker run -d --name portainer --restart unless-stopped \
  -p 9000:9000 -p 9443:9443 -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce
```

### Step 5: Reboot if Needed, Then Verify

If the apt upgrade included a kernel or NVIDIA driver update, reboot now:

```bash
sudo reboot
```

After coming back up:

```bash
nvidia-smi
docker ps
docker compose ls
```

---

## Handling a Post-Upgrade NVIDIA Driver Mismatch

If `nvidia-smi` returns `Failed to initialize NVML: Driver/library version mismatch` after an upgrade, the userspace libraries were updated but the old kernel module is still loaded in memory. This is normal — it resolves on reboot once the new kernel module loads.

Before rebooting, verify DKMS built the new module for your running kernel:

```bash
dkms status
uname -r
```

You want to see your current kernel version listed in the `dkms status` output with status `installed`. If it's there, the reboot will load the correct module and `nvidia-smi` will come up clean.

If the DKMS build is missing, trigger it manually:

```bash
sudo dkms install nvidia/<version> -k $(uname -r)
```

After a clean reboot, GPU containers that failed to start (like Ollama) can be brought up with a standard compose up:

```bash
docker compose -f /path/to/ai-stack/docker-compose.yml up -d
```

---

## Cloudflare Tunnel DNS Gotcha

If you're running a Cloudflare Tunnel in Docker and it loses connectivity after a container restart, the culprit is often Docker's internal DNS resolver (`127.0.0.11`) failing to resolve Cloudflare's `argotunnel.com` SRV records. The fix is to explicitly set DNS servers on the cloudflared service in your compose file:

```yaml
cloudflared:
  image: cloudflare/cloudflared:latest
  dns:
    - 1.1.1.1
    - 8.8.8.8
  # rest of config...
```

Then force recreate the container to apply the change:

```bash
docker compose up -d --force-recreate cloudflared
```

A healthy tunnel should report 4 registered edge connections in its logs:

```bash
docker logs shelter-tunnel --tail 20
```

---

## Quick Reference: Full Update Sequence

```bash
# 1. OS update
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y && sudo apt autoclean

# 2. Pull images (while containers are running)
docker compose -f ~/stack1/docker-compose.yml pull
docker compose -f ~/stack2/docker-compose.yml pull

# 3. Redeploy stacks
docker compose -f ~/stack1/docker-compose.yml up -d --pull always
docker compose -f ~/stack2/docker-compose.yml up -d --pull always

# 4. Update manually managed containers (Portainer example)
docker stop portainer && docker rm portainer
docker pull portainer/portainer-ce
docker run -d --name portainer --restart unless-stopped \
  -p 9000:9000 -p 9443:9443 -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce

# 5. Reboot if kernel/NVIDIA was updated
sudo reboot

# 6. Post-reboot verification
nvidia-smi
docker ps
docker compose ls
```

---

## LVM Expansion Quick Reference

```bash
# After cloning to a larger drive — run in order
sudo pvresize /dev/nvme0n1p3
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv

# Verify
df -h /
```

> **Note:** Adjust `/dev/nvme0n1p3` and `/dev/ubuntu-vg/ubuntu-lv` to match your actual partition and volume group names. Use `lsblk` and `pvdisplay` to confirm.

---

The combination of a clean drive migration and a disciplined update procedure keeps a homelab server running reliably for years. The main gotchas — LVM not expanding automatically, NVIDIA driver/kernel mismatches, and Docker DNS quirks in tunnel containers — are all solvable with the right sequence of commands.
