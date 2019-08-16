## 本地服务部署
## 1. 安装python
    .  https://www.cnblogs.com/beer/p/5557497.html
## 2. 安装mysql
    .  sudo apt-get install mysql-server
## 3. 安装redis
    . sudo apt-get install redis-server
## 4. 安装python依赖库
    . pip install -r requirements.txt
## 6. 配置mysql及redis.
    . 编辑config文件, 修改mysql及redis配置
## 5. 初始化数据库.
    . python db_init.py
## 7. 启动程序
    . sh start.sh
    