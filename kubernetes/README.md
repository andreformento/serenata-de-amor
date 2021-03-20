# Kubernetes

```shell
helm -n okfn-brasil \
     upgrade jarbas \
     -f values-dev.yaml \
     ./helm \
     --install \
     --atomic
```

## References

- [configmap](https://humanitec.com/blog/handling-environment-variables-with-kubernetes)
