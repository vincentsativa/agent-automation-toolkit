# Hermes s6-overlay Container Supervision

## When to use

Load for: adding/removing static services in the Hermes Docker image, diagnosing per-profile gateway startup issues, understanding the Architecture B main-program pattern.

## Architecture

Hermes Docker images use s6-overlay for process supervision. The container's CMD is `/opt/hermes/docker/main-wrapper.sh`, leading-dash args reach the user's program via a shell wrapper.

### Adding a Static Service

1. Create a service directory under `/etc/s6-overlay/s6-rc/svc/<service-name>/`
2. Add a `run` script and `type` file:
```
/etc/s6-overlay/s6-rc/svc/dashboard/
├── run           # executable script
└── type          # contains "longrun"
```
3. Register in `/etc/s6-overlay/s6-rc/contents.d/`

### Profile Gateway Pattern

Each profile has its own gateway process supervised by s6. Debugging steps:
- Check service status: `s6-svstat /run/s6-rc/servicedirs/<profile>-gateway/`
- View logs: `cat /run/s6-rc/servicedirs/<profile>-gateway/log/current`
- Restart: `s6-svc -r /run/s6-rc/servicedirs/<profile>-gateway/`

### Common Pitfalls
- `docker restart` doesn't re-read s6 config, must rebuild the image
- Per-profile gateways inherit the parent container's env but also load profile-specific .env
- Leading-dash args (`-p`, `-s`) need to pass through the main-wrapper.sh correctly