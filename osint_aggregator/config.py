USERNAME_CONCURRENCY = 5
USERNAME_TIMEOUT = 8.0
DOMAIN_TIMEOUT = 8.0
CRTSH_TIMEOUT = 15.0
BREACH_TIMEOUT = 8.0

USERNAME_SITES = [
    {"name": "GitHub",     "url": "https://github.com/{}",                       "method": "status"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/v2/users/{}/",         "method": "status"},
    {"name": "dev.to",     "url": "https://dev.to/api/users/by_username?url={}", "method": "status"},
    {"name": "Steam",      "url": "https://steamcommunity.com/id/{}",            "method": "message", 
     "not_found": "The specified profile could not be found."},
]