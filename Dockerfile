FROM eclipse-temurin:21 AS jre-build

RUN $JAVA_HOME/bin/jlink \
         --add-modules ALL-MODULE-PATH \
         --strip-debug \
         --no-man-pages \
         --no-header-files \
         --output /javaruntime


FROM moelin/1panel:global-latest
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
COPY --from=jre-build /javaruntime $JAVA_HOME

RUN sed -i s@/archive.ubuntu.com/@/mirrors.ustc.edu.cn/@g /etc/apt/sources.list && \
    sed -i s@/security.ubuntu.com/@/mirrors.ustc.edu.cn/@g /etc/apt/sources.list && \
    apt update && apt install software-properties-common -y --no-install-recommends && \
    add-apt-repository ppa:deadsnakes/ppa && apt update && \
    apt install python3.12-venv --no-install-recommends -y && \
    apt clean && rm -rf /var/lib/apt/lists/*
RUN sed -i -e "s#ORIGINAL_USERNAME=.*#ORIGINAL_USERNAME=mc123#g" /usr/local/bin/1pctl && \
    sed -i -e "s#ORIGINAL_PASSWORD=.*#ORIGINAL_PASSWORD=mc123#g" /usr/local/bin/1pctl && \
    python3.12 -m ensurepip --upgrade && \
    python3.12 -m pip install --ignore-installed blinker && \
    python3.12 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    alibabacloud-eci20180808 Flask rcon alibabacloud-sts20150401 alibabacloud-alidns20150109 pydantic

ENV PYTHONPATH="/opt/mc/scripts/"

COPY src /opt/mc/scripts/
WORKDIR /opt/mc/scripts/

CMD ["/bin/bash", "-c", "/usr/local/bin/1panel & sleep 3 && kill $(jobs -p) || true && /app/update_app_version.sh && /usr/local/bin/1pctl reset entrance && /usr/local/bin/1panel & python3.12 /opt/mc/scripts/eci/daemon.py"]