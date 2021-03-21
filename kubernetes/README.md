# Kubernetes

- create application
```shell
helm -n okfn-brasil \
     upgrade jarbas \
     -f values-dev.yaml \
     ./helm \
     --set image.repository=andreformento/serenata-jarbas,image.tag=0.0.2,migrations.run=true \
     --install \
     --atomic
```

- port forward
```shell
kubectl -n okfn-brasil port-forward service/jarbas 8080:80
```

## TODO

- [ ] configmap with dynamic data
- [ ] secrets for database configuration instead configmap
- [ ] populate fake data for local development
- [ ] configure ingress
- [ ] configure nginx
- [ ] validate production environment
- [ ] improve readme

## References

- [configmap](https://humanitec.com/blog/handling-environment-variables-with-kubernetes)
