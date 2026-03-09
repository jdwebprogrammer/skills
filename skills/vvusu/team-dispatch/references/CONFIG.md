# Team Dispatch Config (C option)

## Where

- Built-in default (single source): `~/skills/team-dispatch/config.json`

## Paths

- `paths.projectsRoot` (default: `~/work`)
  - Real code/projects live here.
  - Recommendation: agents create project folders like: `~/work/<project>`
- User override: `~/.openclaw/configs/team-dispatch.json`

Generate user override:
```bash
bash ~/skills/team-dispatch/scripts/setup-config.sh
```

## Goals

- Keep `agentId` portable and stable across machines.
- Allow per-agent presentation and notification routing:
  - `displayName` (human-friendly)
  - `username` (optional)
  - `notify.telegram.chatId` (optional)

## Notification policy

`notifyPolicy`:
- `failures-only` (recommended): only notify on `failed/timeout/blocked`
- `project-complete`: notify when project becomes `completed`
- `all-tasks`: notify on every task completion

## Watcher（后台周期任务）

- `team.watcher.enabled` (default: `true`)
- `team.watcher.backend` (default: `openclaw-cron`)
  - `openclaw-cron`: 默认推荐（统一管理，开箱即用；但会消耗模型 token）
  - `auto-system-first`: 系统调度优先（launchd/systemd/cron），失败才 fallback（更省 token）
  - `launchd|systemd|cron`: 强制指定具体系统调度器
- `team.watcher.interval` (seconds)
- `team.watcher.grace` (seconds)

## Telegram notification

Dispatcher-level behavior (not subagent):
- Based on `notifyPolicy`, when a task/project hits the matching state, the main agent reads config and sends a message to the configured Telegram chat.

Recommended payload:
- project name
- task id
- agentId + displayName
- status + short result/error
- deliverables (paths)

## Example
```json
{
  "team": {
    "agents": {
      "coder": {
        "displayName": "闪电",
        "notify": { "telegram": { "enabled": true, "chatId": "telegram:569110000" } }
      }
    }
  }
}
```
