# AnywhereDoorImsdkWxbot
* imsdk 微信机器人实现

## 部署方式
1. 将代码clone下来
2. 安装docker及buildx
3. 打包镜像
   * `docker buildx build --platform linux/amd64 -t 192.168.25.5:31100/maoyanluo/anywhere-door-imsdk-wxbot:1.0 . --load`
4. 运行容器
   * `docker run --name anywhere-door-imsdk-wxbot -itd -p 8082:80 -e ADMIN_NICKNAME=猫眼螺 -e HOST=192.168.25.7 -e PORT=8081 -e USERNAME=maoyanluo -e TOKEN=1998 -e IMSDK_NAME=wxbot 192.168.25.5:31100/maoyanluo/anywhere-door-imsdk-wxbot:1.0`

## 使用方式
* /login：
  * 返回微信登录二维码，使用手机扫描登录即可，需要占用微信PC登录的设备

## 环境变量
* ADMIN_NICKNAME: 用于交互的微信昵称
* HOST: 控制平面地址
* PORT: 控制平面端口
* PREFIX: 控制平面前缀
* USERNAME: imsdk所属用户
* TOKEN: imsdk令牌
* IMSDK_NAME: imsdk名称