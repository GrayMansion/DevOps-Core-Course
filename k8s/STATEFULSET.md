# StatefulSet Lab Notes

## StatefulSet Overview
StatefulSets are used for applications that need stable identities, ordered operations, and per-pod persistent storage. Compared to Deployments, StatefulSets provide:
- Stable pod names with ordinal indexes (for example, app-0, app-1).
- Stable storage with one PVC per pod from a template.
- Ordered start/stop/update semantics (unless configured otherwise).

Use Deployments for stateless workloads and StatefulSets for stateful workloads such as databases, queues, or clustered services.

## Resource Verification
Run:
```bash
kubectl get po,sts,svc,pvc -o wide
```
Output:
```
NAME                                       READY   STATUS    RESTARTS          AGE   IP            NODE                 NOMINATED NODE   READINESS GATES
pod/devops-info-0                          1/1     Running   0                 22s   10.244.0.41   lab9-control-plane   <none>           <none>
pod/devops-info-1                          1/1     Running   0                 33s   10.244.0.40   lab9-control-plane   <none>           <none>
pod/devops-info-2                          1/1     Running   0                 44s   10.244.0.39   lab9-control-plane   <none>           <none>
pod/devops-info-service-76df4867ff-745zh   1/1     Running   143 (4h58m ago)   42d   10.244.0.14   lab9-control-plane   <none>           <none>
pod/devops-info-service-76df4867ff-fcwfs   1/1     Running   144 (4h58m ago)   42d   10.244.0.13   lab9-control-plane   <none>           <none>
pod/devops-info-service-76df4867ff-mtqhz   1/1     Running   144 (4h58m ago)   42d   10.244.0.27   lab9-control-plane   <none>           <none>
pod/devops-info-service-76df4867ff-scjtv   1/1     Running   144 (4h58m ago)   42d   10.244.0.29   lab9-control-plane   <none>           <none>
pod/devops-info-service-76df4867ff-xklgn   1/1     Running   144 (4h58m ago)   42d   10.244.0.30   lab9-control-plane   <none>           <none>

NAME                           READY   AGE     CONTAINERS    IMAGES
statefulset.apps/devops-info   3/3     3m33s   devops-info   graymansion/devops-info-service:lab02

NAME                           TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE     SELECTOR
service/devops-info            ClusterIP   10.96.108.140   <none>        80/TCP         3m12s   app.kubernetes.io/instance=devops-info,app.kubernetes.io/name=devops-info
service/devops-info-headless   ClusterIP   None            <none>        80/TCP         3m33s   app.kubernetes.io/instance=devops-info,app.kubernetes.io/name=devops-info
service/devops-info-service    NodePort    10.96.58.156    <none>        80:30080/TCP   42d     app=devops-info-service
service/kubernetes             ClusterIP   10.96.0.1       <none>        443/TCP        42d     <none>

NAME                                              STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE     VOLUMEMODE
persistentvolumeclaim/data-volume-devops-info-0   Bound    pvc-f9b53d3b-c56c-4a0a-b54c-90f4f66f5e55   100Mi      RWO            standard       <unset>                 3m33s   Filesystem
persistentvolumeclaim/data-volume-devops-info-1   Bound    pvc-8edf6b4f-e628-4912-bd77-e661bb17aeb4   100Mi      RWO            standard       <unset>                 3m22s   Filesystem
persistentvolumeclaim/data-volume-devops-info-2   Bound    pvc-41f1769f-3535-422e-939b-8a1cdc00f224   100Mi      RWO            standard       <unset>                 3m11s   Filesystem
```

## Network Identity (Headless Service)
Run:
```bash
kubectl exec -it devops-info-0 -- /bin/sh -c "getent hosts devops-info-1.devops-info-headless"
```
Note: `nslookup` was not available in the container image, so `getent hosts` was used for DNS verification.
Output:
```
10.244.0.40     devops-info-1.devops-info-headless.default.svc.cluster.local
```

DNS naming pattern observed:
```
<pod-name>.<headless-service-name>.<namespace>.svc.cluster.local
```

## Per-Pod Storage Evidence
Run:
```bash
kubectl exec devops-info-0 -- /bin/sh -c "echo 5 > /data/visits && cat /data/visits"
kubectl exec devops-info-1 -- /bin/sh -c "echo 9 > /data/visits && cat /data/visits"
```
Note: the running image did not expose a `/visits` endpoint, so visit counts were written and read directly from `/data/visits` to demonstrate per-pod storage isolation.
Output:
```
devops-info-0 /data/visits -> 5
devops-info-1 /data/visits -> 9
```

## Persistence Test
Run:
```bash
kubectl exec devops-info-0 -- cat /data/visits
kubectl delete pod devops-info-0
kubectl wait --for=condition=ready pod/devops-info-0
kubectl exec devops-info-0 -- cat /data/visits
```
Output:
```
Before: 5
After: 5
```