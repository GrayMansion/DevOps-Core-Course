# Argo Rollouts - Progressive Delivery Report

## 1. Argo Rollouts Setup

Installation and verification commands:

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

❯ kubectl argo rollouts version
kubectl-argo-rollouts: v1.9.0+838d4e7
	BuildDate: 2026-03-20T21:08:11Z
	GitCommit: 838d4e792be666ec11bd0c80331e0c5511b5010e
	GitTreeState: clean
	GoVersion: go1.24.13
	Compiler: gc
	Platform: linux/amd64
```

Rollout vs Deployment key differences:
- `Rollout` adds `strategy.canary` and `strategy.blueGreen` for progressive delivery.
- `Rollout` integrates analysis steps and automated rollback.
- Pod template, selectors, and metadata are otherwise aligned with `Deployment`.

## 2. Canary Deployment

Helm rollout template: [k8s/devops-info/templates/rollout.yaml](k8s/devops-info/templates/rollout.yaml)

Canary steps implemented:
- 20 percent traffic, then manual pause
- 40 percent, pause 30s
- 60 percent, pause 30s
- 80 percent, pause 30s
- 100 percent

Optional analysis step:
- Enabled by `analysisTemplate.enabled: true` and `rollout.canary.analysis.enabled: true`
- Uses `/health` and checks `$.status == "healthy"`

Deploy and test (example):

```bash
# Canary install
helm upgrade --install devops-info k8s/devops-info \
	-f k8s/devops-info/values-rollout-canary.yaml \
	--set service.type=ClusterIP

# Trigger a rollout
helm upgrade devops-info k8s/devops-info \
	-f k8s/devops-info/values-rollout-canary.yaml \
	--set service.type=ClusterIP \
	--set appConfig.environment=canary1 \
	--set securityContext.runAsNonRoot=false \
	--reset-values

# Watch rollout
kubectl argo rollouts get rollout devops-info

# Promote after manual pause
kubectl argo rollouts promote devops-info

# Abort rollback test
kubectl argo rollouts abort devops-info
```

Note: `service.type=ClusterIP` avoids a NodePort collision, and `securityContext.runAsNonRoot=false` is required because the image user is non-numeric.

Evidence to capture:
- Dashboard screenshots for each step (20, 40, 60, 80, 100)
- CLI output from `kubectl argo rollouts get rollout devops-info -w`

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

❯ kubectl argo rollouts promote devops-info
rollout 'devops-info' promoted

❯ kubectl argo rollouts abort devops-info
rollout 'devops-info' aborted
```

## 3. Blue-Green Deployment

Helm values: [k8s/devops-info/values-rollout-bluegreen.yaml](k8s/devops-info/values-rollout-bluegreen.yaml)

Blue-green configuration:
- Active service: `devops-info`
- Preview service: `devops-info-preview`
- Manual promotion with `autoPromotionEnabled: false`

Deploy and test (example):

```bash
# Blue-green install
helm upgrade devops-info k8s/devops-info \
	-f k8s/devops-info/values-rollout-bluegreen.yaml \
	--set service.type=ClusterIP \
	--set appConfig.environment=bluegreen1 \
	--set securityContext.runAsNonRoot=false \
	--reset-values

# Preview service
kubectl port-forward svc/devops-info-preview 8081:80

# Promote to active
kubectl argo rollouts promote devops-info

# Roll back
kubectl argo rollouts undo devops-info
```

Evidence to capture:
- Preview service response via port-forward
- Dashboard view showing active and preview services

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

❯ kubectl argo rollouts undo devops-info
rollout 'devops-info' undo
```

## 4. Strategy Comparison

Canary:
- Gradual traffic shift, safer for unknown changes.
- Lower resource cost than blue-green.
- Rollback is still fast but not instant for every step.

Blue-Green:
- Instant switch by swapping services.
- Requires double capacity during rollout.
- Best for quick cutover and easy rollback.

Recommendation:
- Use canary for risky changes or large user bases.
- Use blue-green for fast, predictable cutovers.

## 5. CLI Commands Reference

```bash
# Status and watch
kubectl argo rollouts get rollout devops-info -w

# Promotion
kubectl argo rollouts promote devops-info

# Abort or rollback
kubectl argo rollouts abort devops-info
kubectl argo rollouts undo devops-info

# Retry an aborted rollout
kubectl argo rollouts retry devops-info
```
