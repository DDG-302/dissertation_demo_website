# Build指令
[docker build命令详解-CSDN博客](https://blog.csdn.net/Mantou023/article/details/135008936)

docker build -t dd_streamlit .

# 清理
Docker提供了一些命令来清理资源，如容器、镜像、卷、网络等。以下是一些常用的命令：

- 清理停止的容器：

```
docker container prune
```

- 清理未使用的镜像：

```
docker image prune
```



- 清理未使用的卷：

```
docker volume prune
```

- 清理未使用的网络：

```
docker network prune
```

- 清理所有未使用的对象（包括容器、镜像、卷和网络）：

```
docker system prune
```

- 清理所有未使用的对象，包括悬空的镜像、停止的容器和未被任何容器使用的网络和卷：

```
docker system prune -a
```

