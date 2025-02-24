# AnywhereDoorImsdkWxbot
* imsdk 微信机器人实现
* 依赖gewechat
  * 详见: https://github.com/Devo919/Gewechat & https://github.com/mikoshu/gewechaty
  * 容器使用了二次打包的：registry.cn-chengdu.aliyuncs.com/tu1h/wechotd:alpine

## 使用方式
* 保证gewechat正常启动
* /login：
  * 返回微信登录二维码，使用手机扫描登录即可，需要占用微信PC登录的设备

## 环境变量
* ADMIN_WXID: 用于交互的微信号
* HOST: 控制平面地址
* PORT: 控制平面端口
* PREFIX: 控制平面前缀
* USERNAME: imsdk所属用户名称
* TOKEN: imsdk令牌
* IMSDK_NAME: imsdk名称
* API_GEWE: gewe的地址, 即http://gewechat-ip:端口
* WX_COLLECT: 接收消息回调的地址, 即当前容器的http://ip:端口

## 打包方式
1. 将代码clone下来
2. 安装docker及buildx
3. 打包镜像
   * `docker buildx build --platform linux/amd64 -t 192.168.25.5:31100/maoyanluo/anywhere-door-imsdk-wxbot:1.0 . --load`

## 部署方式

### Docker Command Line
1. 运行容器
   * `docker run --name anywhere-door-imsdk-wxbot -itd -p 8082:80 -e ADMIN_WXID=admin_username -e HOST=ip -e PORT=port -e USERNAME=username -e TOKEN=token -e IMSDK_NAME=wxbot -e API_GEWE=http://gewechat-ip:端口 -e WX_COLLECT=http://ip:端口 -v /home/maoyanluo/volume/session:/ws/src/session --restart=always 192.168.25.5:31100/maoyanluo/anywhere-door-imsdk-wxbot:1.0`

### Kubernetes
* 主配置文件
```yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: anywhere-door-imsdk-wxbot-pvc
  namespace: anywhere-door
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: "smb-anywhere-door"
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: anywhere-door-imsdk-wxbot-statefulset
  namespace: anywhere-door
spec:
  replicas: 1
  selector:
    matchLabels:
      app: anywhere-door-imsdk-wxbot
  template:
    metadata:
      labels:
        app: anywhere-door-imsdk-wxbot
    spec:
      containers:
      - name: anywhere-door-imsdk-wxbot
        image: 192.168.25.5:31100/maoyanluo/anywhere-door-imsdk-wxbot:1.0
        imagePullPolicy: IfNotPresent
        env:
        - name: ADMIN_WXID
          value: "admin_name"
        - name: HOST
          value: "anywhere-door-control-plane-service.anywhere-door"
        - name: PORT
          value: "80"
        - name: USERNAME
          value: "username"
        - name: TOKEN
          value: "token"
        - name: IMSDK_NAME
          value: "wxbot"
        - name: API_GEWE
          value: "http://gewe-wxbot-service.person-app:2531"
        - name: WX_COLLECT
          value: "http://anywhere-door-imsdk-wxbot-service.anywhere-door:80"
        ports:
        - containerPort: 80
        volumeMounts:
        - name: anywhere-door-imsdk-wxbot-storage
          mountPath: /ws/src/session
      restartPolicy: Always
      volumes:
        - name: anywhere-door-imsdk-wxbot-storage
          persistentVolumeClaim:
            claimName: anywhere-door-imsdk-wxbot-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: anywhere-door-imsdk-wxbot-service
  namespace: anywhere-door
  labels:
    app: anywhere-door-imsdk-wxbot
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: anywhere-door-imsdk-wxbot
```
* 首次使用需要额外暴露如下服务, 登录成功后, 需要将该服务删除(强烈推荐, 为了安全起见, imsdk不应该向集群外暴露服务, 登录这个接口也是无奈之举)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: anywhere-door-imsdk-wxbot-service-export
  namespace: anywhere-door
  labels:
    app: anywhere-door-imsdk-wxbot
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 20081
  selector:
    app: anywhere-door-imsdk-wxbot
```

## 使用方式
1. 保证容器正常运行, 并且启动后, 扫码登录成功
2. 注册imsdk: POST AnywhereDoorManager/imsdk/create & Header: token: token & Body: { "imsdk_name": "name", "imsdk_describe": "desc", "imsdk_host": "anywhere-door-imsdk-wxbot-service.anywhere-door", "imsdk_port": 80, "imsdk_token": "token" }