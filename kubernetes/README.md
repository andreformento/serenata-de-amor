# Kubernetes

```shell
helm -n okfn-brasil \
     upgrade jarbas \
     -f values-dev.yaml \
     ./helm \
     --set image.repository=andreformento/serenata-jarbas,image.tag=0.0.2,migrations.run=true \
     --install \
     --atomic
```

## References

- [configmap](https://humanitec.com/blog/handling-environment-variables-with-kubernetes)
