# LAB14 Report - Progressive Delivery with Argo Rollouts

## Summary

This lab adds Argo Rollouts to the `devops-info` Helm chart and documents canary and blue-green strategies with optional automated analysis.

Key files:
- [k8s/devops-info/templates/rollout.yaml](k8s/devops-info/templates/rollout.yaml)
- [k8s/devops-info/templates/service-preview.yaml](k8s/devops-info/templates/service-preview.yaml)
- [k8s/devops-info/templates/analysis-template.yaml](k8s/devops-info/templates/analysis-template.yaml)
- [k8s/devops-info/values-rollout-canary.yaml](k8s/devops-info/values-rollout-canary.yaml)
- [k8s/devops-info/values-rollout-bluegreen.yaml](k8s/devops-info/values-rollout-bluegreen.yaml)
- [k8s/ROLLOUTS.md](k8s/ROLLOUTS.md)

## Task 1 - Argo Rollouts Fundamentals

Commands used:

```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/dashboard-install.yaml
kubectl port-forward svc/argo-rollouts-dashboard -n argo-rollouts 3100:3100
kubectl argo rollouts version
```

Console evidence:

```text
❯ kubectl get pods -n argo-rollouts
NAME                                       READY   STATUS    RESTARTS   AGE
argo-rollouts-79b89d8856-p8cvv             1/1     Running   0          36s
argo-rollouts-dashboard-7b7bf46775-ggg8k   1/1     Running   0          27s

❯ kubectl get svc -n argo-rollouts
NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
argo-rollouts-dashboard   ClusterIP   10.96.57.77    <none>        3100/TCP   27s
argo-rollouts-metrics     ClusterIP   10.96.175.27   <none>        8090/TCP   36s

❯ kubectl argo rollouts version
kubectl-argo-rollouts: v1.9.0+838d4e7
  BuildDate: 2026-03-20T21:08:11Z
  GitCommit: 838d4e792be666ec11bd0c80331e0c5511b5010e
  GitTreeState: clean
  GoVersion: go1.24.13
  Compiler: gc
  Platform: linux/amd64
```

Rollout vs Deployment:
- `Rollout` adds canary and blue-green strategies.
- `Rollout` supports analysis steps and automated rollback.
- Base pod template and selector structure stay consistent.

## Task 2 - Canary Deployment

Canary strategy (20, pause, 40, 60, 80, 100) is defined in [k8s/devops-info/templates/rollout.yaml](k8s/devops-info/templates/rollout.yaml).

Commands used:

```bash
helm upgrade --install devops-info k8s/devops-info \
  -f k8s/devops-info/values-rollout-canary.yaml \
  --set service.type=ClusterIP

# Trigger a new rollout by changing config
helm upgrade devops-info k8s/devops-info \
  -f k8s/devops-info/values-rollout-canary.yaml \
  --set service.type=ClusterIP \
  --set appConfig.environment=canary1 \
  --set securityContext.runAsNonRoot=false \
  --reset-values

kubectl argo rollouts get rollout devops-info
kubectl argo rollouts promote devops-info
kubectl argo rollouts abort devops-info
```

Note: I used `service.type=ClusterIP` because NodePort `30080` was already allocated, and set `securityContext.runAsNonRoot=false` because the image uses a non-numeric user (`appuser`).

Console evidence:

```text
❯ kubectl argo rollouts get rollout devops-info
Name:            devops-info
Namespace:       default
Status:          ◌ Progressing
Message:         more replicas need to be updated
Strategy:        Canary
  Step:          5/10
  SetWeight:     60
  ActualWeight:  100
Images:          graymansion/devops-info-service:lab02 (canary, stable)
Replicas:
  Desired:       3
  Current:       4
  Updated:       2
  Ready:         1
  Available:     1

NAME                                     KIND         STATUS                        AGE    INFO
⟳ devops-info                            Rollout      ◌ Progressing                 4m34s
├──# revision:3
│  ├──⧉ devops-info-789cd99776           ReplicaSet   ◌ Progressing                 76s    canary
│  │  ├──□ devops-info-789cd99776-mb2s7  Pod          ✔ Running                     76s    ready:1/1
│  │  └──□ devops-info-789cd99776-5sk8d  Pod          ✔ Running                     2s     ready:0/1
│  └──α devops-info-789cd99776-3-1       AnalysisRun  ✔ Successful                  76s    ✔ 3,⚠ 2
└──# revision:1
   └──⧉ devops-info-79f6db9cd7           ReplicaSet   ◌ Progressing                 4m34s  stable

❯ kubectl argo rollouts promote devops-info
rollout 'devops-info' promoted

❯ kubectl argo rollouts abort devops-info
rollout 'devops-info' aborted
```

## Task 3 - Blue-Green Deployment

Blue-green strategy uses active and preview services:
- Active: `devops-info`
- Preview: `devops-info-preview`

Commands used:

```bash
helm upgrade devops-info k8s/devops-info \
  -f k8s/devops-info/values-rollout-bluegreen.yaml \
  --set service.type=ClusterIP \
  --set appConfig.environment=bluegreen1 \
  --set securityContext.runAsNonRoot=false \
  --reset-values

kubectl get svc -n default | grep devops-info
kubectl port-forward svc/devops-info 8080:80
kubectl port-forward svc/devops-info-preview 8081:80
kubectl argo rollouts promote devops-info
kubectl argo rollouts undo devops-info
```

Console evidence:

```text
❯ kubectl get svc -n default | grep devops-info
devops-info           ClusterIP   10.96.249.12   <none>        80/TCP         7m
devops-info-preview   ClusterIP   10.96.198.66   <none>        80/TCP         113s
devops-info-service   NodePort    10.96.58.156   <none>        80:30080/TCP   35d

❯ kubectl argo rollouts get rollout devops-info
Name:            devops-info
Namespace:       default
Status:          ✔ Healthy
Strategy:        BlueGreen
Images:          graymansion/devops-info-service:lab02 (stable, active)
Replicas:
  Desired:       3
  Current:       3
  Updated:       3
  Ready:         3
  Available:     3

❯ kubectl argo rollouts promote devops-info
rollout 'devops-info' promoted

❯ kubectl argo rollouts undo devops-info
rollout 'devops-info' undo

❯ kubectl argo rollouts get rollout devops-info
Status:          ॥ Paused
Message:         BlueGreenPause
Strategy:        BlueGreen
Images:          graymansion/devops-info-service:lab02 (active, preview, stable)
```

## Task 4 - Documentation

Progressive delivery documentation is in [k8s/ROLLOUTS.md](k8s/ROLLOUTS.md).

## Bonus - Automated Analysis

Optional analysis uses a web provider to check `/health` and verify `$.status == "healthy"`.

Enable with:

```bash
helm upgrade --install devops-info k8s/devops-info \
  -f k8s/devops-info/values-rollout-canary.yaml \
  --set analysisTemplate.enabled=true \
  --set rollout.canary.analysis.enabled=true
```

Evidence to capture:
- `kubectl argo rollouts get rollout devops-info -w`
- Analysis status in the dashboard
