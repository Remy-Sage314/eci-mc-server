FROM eclipse-temurin:21 AS jre-build

RUN $JAVA_HOME/bin/jlink \
         --add-modules ALL-MODULE-PATH \
         --strip-debug \
         --no-man-pages \
         --no-header-files \
         --output /javaruntime


FROM python:3.13-slim-bookworm
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
COPY --from=jre-build /javaruntime $JAVA_HOME

ENV PYTHONPATH="/opt/mc/scripts/"
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    alibabacloud-eci20180808 Flask rcon alibabacloud-sts20150401 alibabacloud-alidns20150109 pydantic
COPY src /opt/mc/scripts/
WORKDIR /opt/mc/scripts/

CMD python /opt/mc/scripts/eci/daemon.py
