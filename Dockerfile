FROM registry.cn-hangzhou.aliyuncs.com/company-bycx/smart-collection:v2
MAINTAINER shaoxin <shaoxin@9ffenqigo.com>
# 设置环境变量
ENV APP_ROOT=/sjb/smart_collection
ENV SMART_COLLECTION_ENV=DEV
ENV C_FORCE_ROOT=true
ENV WORKERS=2
ENV ZK_HOSTS=10.46.229.33:3181,10.46.229.17:3181,10.46.225.70:3181
# 端口映射
EXPOSE 8002 8002
EXPOSE 9099 9099
EXPOSE 9098 9098

WORKDIR ${APP_ROOT}/
COPY /sjb/smart_collection ${APP_ROOT}/
# 安装依赖
RUN pip install --upgrade pip
RUN pip install -r ${APP_ROOT}/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
ENV TIME_ZONE=Asia/Shanghai
RUN echo "${TIME_ZONE}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime
RUN find . -name "*.pyc" -delete
RUN find . -name "gunicorn.pid" -delete
CMD sh ${APP_ROOT}/run/start.sh
